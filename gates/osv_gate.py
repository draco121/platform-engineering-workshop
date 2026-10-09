#!/usr/bin/env python3
"""
osv_gate.py - a tiny "security gate" for Java (Maven) projects.

What it does, in four steps:
  1. Find the dependencies          (depreader.py)
  2. Ask OSV.dev "are any of these vulnerable?"   (one batch request)
  3. Look up the details of each vulnerability    (severity + which version fixes it)
  4. Decide: PASS (exit 0) or BLOCK the release (exit 1)

That exit code is the whole trick: a CI pipeline stops when a step exits non-zero.
So this ~250-line script is a real deployment gate.

Usage:
  python osv_gate.py ../demo-app/pom.xml
  python osv_gate.py ../demo-app/pom.xml --fail-on CRITICAL
  python osv_gate.py --deps-file deps.txt              # full transitive tree from Maven
  python osv_gate.py ../demo-app/pom.xml --json-out report.json

OSV API docs: https://google.github.io/osv.dev/api/
Standard library only - no pip install needed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import depreader

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
OSV_VULN_URL = "https://api.osv.dev/v1/vulns/{id}"

SEVERITY_ORDER = ["UNKNOWN", "LOW", "MODERATE", "HIGH", "CRITICAL"]

# ---------------------------------------------------------------- pretty output
_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_PAINT = {"CRITICAL": "\033[1;37;41m", "HIGH": "\033[1;31m", "MODERATE": "\033[33m",
          "LOW": "\033[36m", "UNKNOWN": "\033[2m", "OK": "\033[32m", "BOLD": "\033[1m"}


def paint(text: str, style: str) -> str:
    return f"{_PAINT[style]}{text}\033[0m" if _COLOR else text


# ---------------------------------------------------------------- HTTP helpers
def post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


# ---------------------------------------------------------------- step 2: ask OSV
def query_osv(deps: list[depreader.Dependency]) -> dict[str, list[str]]:
    """One request for all packages. Returns {"group:artifact@version": [vuln ids]}."""
    queries = [{"package": {"ecosystem": "Maven", "name": d.name}, "version": d.version}
               for d in deps]
    results = post_json(OSV_BATCH_URL, {"queries": queries})["results"]
    # OSV guarantees the results come back in the same order as the queries.
    return {str(d): [v["id"] for v in r.get("vulns", [])] for d, r in zip(deps, results)}


# ---------------------------------------------------------------- step 3: details
def cvss3_base_score(vector: str) -> float | None:
    """Compute a CVSS v3.x base score from its vector string (FIRST.org formula)."""
    try:
        m = dict(part.split(":") for part in vector.split("/")[1:])
        av = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}[m["AV"]]
        ac = {"L": 0.77, "H": 0.44}[m["AC"]]
        ui = {"N": 0.85, "R": 0.62}[m["UI"]]
        changed = m["S"] == "C"
        pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[m["PR"]]
        cia = {"H": 0.56, "L": 0.22, "N": 0.0}
        iss = 1 - (1 - cia[m["C"]]) * (1 - cia[m["I"]]) * (1 - cia[m["A"]])
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
        if impact <= 0:
            return 0.0
        exploit = 8.22 * av * ac * pr * ui
        raw = min(1.08 * (impact + exploit), 10) if changed else min(impact + exploit, 10)
        return math.ceil(raw * 10 - 1e-9) / 10
    except (KeyError, ValueError):
        return None


def score_to_label(score: float) -> str:
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MODERATE"
    return "LOW" if score > 0 else "UNKNOWN"


def severity_of(vuln: dict) -> str:
    """GitHub advisories carry a ready-made label; otherwise compute it from CVSS."""
    label = (vuln.get("database_specific") or {}).get("severity")
    if label:
        label = label.upper()
        return "MODERATE" if label == "MEDIUM" else label
    for sev in vuln.get("severity", []):
        if sev.get("type", "").startswith("CVSS_V3"):
            score = cvss3_base_score(sev["score"])
            if score is not None:
                return score_to_label(score)
    return "UNKNOWN"


def version_key(v: str) -> tuple:
    """Good-enough Maven version ordering: 2.9.10.1 > 2.9.10 > 2.9.10-rc1."""
    key = []
    for tok in re.split(r"[.\-_]", v.lower()):
        if tok.isdigit():
            key.append((1, int(tok), ""))
        elif tok in ("final", "ga", "release"):
            continue
        else:
            key.append((0, 0, tok))  # qualifiers (alpha, beta, rc) sort before releases
    key.append((0.5, 0, ""))  # so that 1.0 > 1.0-rc1 but 1.0.1 > 1.0
    return tuple(key)


def first_fix_after(vuln: dict, dep: depreader.Dependency) -> str | None:
    """The smallest 'fixed' version that is newer than the one we use."""
    fixes = []
    for affected in vuln.get("affected", []):
        if affected.get("package", {}).get("name") != dep.name:
            continue
        for rng in affected.get("ranges", []):
            for event in rng.get("events", []):
                fixed = event.get("fixed")
                if fixed and version_key(fixed) > version_key(dep.version):
                    fixes.append(fixed)
    return min(fixes, key=version_key) if fixes else None


def fetch_details(ids: set[str]) -> dict[str, dict]:
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = pool.map(lambda i: get_json(OSV_VULN_URL.format(id=i)), sorted(ids))
        return {r["id"]: r for r in records}


# ---------------------------------------------------------------- exceptions file
def load_ignores(path: str) -> dict[str, dict]:
    """
    .osv-ignore.json lets a team accept a risk *on purpose*, with a reason and an expiry:
      [{"id": "GHSA-xxxx", "reason": "not reachable, see ticket SEC-12", "expires": "2026-12-31"}]
    Expired entries are ignored, so exceptions cannot quietly live forever.
    """
    if not os.path.exists(path):
        return {}
    today = dt.date.today().isoformat()
    with open(path, encoding="utf-8") as fh:
        entries = json.load(fh)
    return {e["id"]: e for e in entries if e.get("expires", "9999-12-31") >= today}


# ---------------------------------------------------------------- step 4: decide
def main() -> int:
    ap = argparse.ArgumentParser(description="Block releases that ship known-vulnerable libraries.")
    ap.add_argument("pom", nargs="?", default="pom.xml", help="path to pom.xml")
    ap.add_argument("--deps-file", help="output of `mvn dependency:list -DoutputFile=...`")
    ap.add_argument("--fail-on", default="HIGH", choices=SEVERITY_ORDER[1:],
                    help="block the release at this severity or above (default: HIGH)")
    ap.add_argument("--ignore-file", default=".osv-ignore.json")
    ap.add_argument("--json-out", help="also write a machine-readable report here")
    args = ap.parse_args()

    print(paint("\n== OSV security gate ==", "BOLD"))
    deps = depreader.load(args.pom, args.deps_file)
    print(f"Scanning {len(deps)} dependencies against OSV.dev ...\n")

    hits = query_osv(deps)
    details = fetch_details({i for ids in hits.values() for i in ids})
    ignores = load_ignores(args.ignore_file)
    threshold = SEVERITY_ORDER.index(args.fail_on)

    blocking, report = 0, []
    for dep in deps:
        ids = hits[str(dep)]
        if not ids:
            print(f"  {paint('OK ', 'OK')} {dep}")
            report.append({"package": str(dep), "vulnerabilities": []})
            continue

        vulns = []
        for vid in ids:
            v = details[vid]
            cve = next((a for a in v.get("aliases", []) if a.startswith("CVE-")), "")
            vulns.append({"id": vid, "cve": cve, "severity": severity_of(v),
                          "summary": (v.get("summary") or v.get("details", ""))[:90],
                          "fixed_in": first_fix_after(v, dep),
                          "ignored": vid in ignores})
        vulns.sort(key=lambda x: SEVERITY_ORDER.index(x["severity"]), reverse=True)

        worst = vulns[0]["severity"]
        fixes = [x["fixed_in"] for x in vulns if x["fixed_in"]]
        upgrade = max(fixes, key=version_key) if fixes else None
        print(f"  {paint('VULN', worst)} {dep}  -  {len(vulns)} known issue(s), worst: {worst}")
        for x in vulns[:5]:
            tag = " (accepted risk)" if x["ignored"] else ""
            print(f"         {paint(x['severity'].ljust(8), x['severity'])} {x['id']:<20} "
                  f"{x['cve']:<16} {x['summary']}{tag}")
        if len(vulns) > 5:
            print(f"         ... and {len(vulns) - 5} more")
        if upgrade:
            print(f"         {paint('FIX', 'OK')}: upgrade to {upgrade} or later")
        else:
            print(f"         {paint('FIX', 'MODERATE')}: no fixed version published - replace or mitigate")

        blocking += sum(1 for x in vulns
                        if not x["ignored"] and SEVERITY_ORDER.index(x["severity"]) >= threshold)
        report.append({"package": str(dep), "recommended_upgrade": upgrade, "vulnerabilities": vulns})

    total = sum(len(r["vulnerabilities"]) for r in report)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"tool": "osv_gate", "fail_on": args.fail_on, "total": total,
                       "blocking": blocking, "packages": report}, fh, indent=2)

    print()
    if blocking:
        print(paint(f"GATE: BLOCKED - {blocking} issue(s) at {args.fail_on} or above "
                    f"({total} total). Fix them, or record an accepted risk.", "CRITICAL"))
        return 1
    print(paint(f"GATE: PASSED - nothing at {args.fail_on} or above ({total} lower-severity "
                f"issue(s) noted).", "OK"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
