#!/usr/bin/env python3
"""
license_gate.py - a "license gate" for Java (Maven) projects.

Every open-source library comes with a license: the legal rules for using it.
Most are friendly (MIT, Apache-2.0). Some are "copyleft" (GPL, AGPL): ship them
inside your product and you may be required to publish YOUR source code too.

This gate:
  1. Finds the dependencies                        (depreader.py)
  2. Asks deps.dev which license each version has  (Google's Open Source Insights)
  3. Compares each license against license-policy.json  -> ALLOW / REVIEW / DENY
  4. Exits 1 (blocks the release) if anything is DENY
     (add --strict to also block on REVIEW)

Usage:
  python license_gate.py ../demo-app/pom.xml
  python license_gate.py ../demo-app/pom.xml --strict
  python license_gate.py --deps-file deps.txt --json-out licenses.json

deps.dev API docs: https://docs.deps.dev/api/v3/
Standard library only - no pip install needed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import depreader

DEPS_DEV_URL = "https://api.deps.dev/v3/systems/maven/packages/{name}/versions/{version}"
RISK = ["ALLOW", "REVIEW", "DENY"]

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_PAINT = {"ALLOW": "\033[32m", "REVIEW": "\033[33m", "DENY": "\033[1;37;41m", "BOLD": "\033[1m"}


def paint(text: str, style: str) -> str:
    return f"{_PAINT[style]}{text}\033[0m" if _COLOR else text


# ---------------------------------------------------------------- step 2: look up
def licenses_for(dep: depreader.Dependency) -> list[str]:
    url = DEPS_DEV_URL.format(name=urllib.parse.quote(dep.name, safe=""),
                              version=urllib.parse.quote(dep.version, safe=""))
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.load(resp).get("licenses") or ["UNKNOWN"]
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return ["UNKNOWN"]
        raise


# ---------------------------------------------------------------- step 3: classify
def load_policy(path: str) -> tuple[dict[str, str], dict[str, dict]]:
    """
    Returns (lookup, overrides):
      lookup    = {"MIT": "ALLOW", "GPL-3.0": "DENY", ...}
      overrides = {"group:artifact": {"license": "MIT", "evidence": "..."}}
    """
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    lookup = {}
    for bucket in ("allow", "review", "deny"):
        for lic in raw[bucket]["licenses"]:
            lookup[lic.upper()] = bucket.upper()
    overrides = raw.get("overrides", {}).get("packages", {})
    return lookup, overrides


def classify_id(license_id: str, policy: dict[str, str]) -> str:
    """One SPDX id -> ALLOW / REVIEW / DENY. Anything unknown needs a human: REVIEW."""
    return policy.get(license_id.strip("() ").upper(), "REVIEW")


def classify_expression(expr: str, policy: dict[str, str]) -> str:
    """
    SPDX expressions combine licenses:
      "MIT OR GPL-2.0"   -> you may CHOOSE either, so take the friendliest  (min risk)
      "MIT AND GPL-2.0"  -> you must obey BOTH,      so take the strictest  (max risk)
      "GPL-2.0 WITH Classpath-exception-2.0" -> an exception softens the license
    """
    expr = expr.strip()
    if " OR " in expr:
        return min((classify_expression(p, policy) for p in expr.split(" OR ")), key=RISK.index)
    if " AND " in expr:
        return max((classify_expression(p, policy) for p in expr.split(" AND ")), key=RISK.index)
    if " WITH " in expr:
        base, exception = expr.split(" WITH ", 1)
        combined = f"{base.strip('() ')}-with-{exception.split('-exception')[0].strip('() ')}-exception"
        verdict = policy.get(combined.upper())
        return verdict or max(classify_id(base, policy), "REVIEW", key=RISK.index)
    return classify_id(expr, policy)


def verdict_for(licenses: list[str], policy: dict[str, str]) -> str:
    # A package listing several licenses must satisfy all of them.
    return max((classify_expression(lic, policy) for lic in licenses), key=RISK.index)


# ---------------------------------------------------------------- step 4: decide
def main() -> int:
    ap = argparse.ArgumentParser(description="Block releases that ship libraries with risky licenses.")
    ap.add_argument("pom", nargs="?", default="pom.xml")
    ap.add_argument("--deps-file", help="output of `mvn dependency:list -DoutputFile=...`")
    ap.add_argument("--policy", default=os.path.join(os.path.dirname(__file__), "license-policy.json"))
    ap.add_argument("--strict", action="store_true", help="also block on REVIEW")
    ap.add_argument("--json-out")
    args = ap.parse_args()

    print(paint("\n== License gate ==", "BOLD"))
    policy, overrides = load_policy(args.policy)
    deps = depreader.load(args.pom, args.deps_file)
    print(f"Checking licenses of {len(deps)} dependencies via deps.dev ...\n")

    with ThreadPoolExecutor(max_workers=8) as pool:
        found = list(pool.map(licenses_for, deps))

    counts = {r: 0 for r in RISK}
    report = []
    for dep, lics in zip(deps, found):
        note = ""
        if dep.name in overrides:
            lics = [overrides[dep.name]["license"]]
            note = "  (manual override - see policy evidence)"
        verdict = verdict_for(lics, policy)
        counts[verdict] += 1
        report.append({"package": str(dep), "licenses": lics, "verdict": verdict,
                       "overridden": bool(note)})
        print(f"  {paint(verdict.ljust(6), verdict)} {str(dep):<55} {' | '.join(lics)}{note}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"tool": "license_gate", "counts": counts, "packages": report}, fh, indent=2)

    print(f"\n  allow: {counts['ALLOW']}   review: {counts['REVIEW']}   deny: {counts['DENY']}")
    blocked = counts["DENY"] or (args.strict and counts["REVIEW"])
    if blocked:
        print(paint("GATE: BLOCKED - replace the DENY packages (or get written approval from legal).", "DENY"))
        return 1
    if counts["REVIEW"]:
        print(paint("GATE: PASSED with warnings - someone should review the REVIEW packages.", "REVIEW"))
    else:
        print(paint("GATE: PASSED - all licenses are on the allow list.", "ALLOW"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
