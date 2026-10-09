#!/usr/bin/env python3
"""
LAB 1 STARTER - build your own security gate in ~20 lines of your code.

Run it:      python starter_osv_gate.py ../demo-app/pom.xml
Stuck?       The finished version is osv_gate.py in this folder. Try not to peek too early!

There are 3 TODOs. Each one is a mission in labs/LAB-1-security-gate.md.
"""

import json
import sys
import urllib.request
from functools import lru_cache

import depreader

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
OSV_VULN_URL = "https://api.osv.dev/v1/vulns/{id}"
SEVERITY_ORDER = ["UNKNOWN", "LOW", "MODERATE", "HIGH", "CRITICAL"]
FAIL_ON = "HIGH"


def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


@lru_cache(maxsize=None)  # remember answers so we never download the same record twice
def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


# --------------------------------------------------------------------------- MISSION 1
def build_query(dep):
    """
    TODO 1: Return ONE OSV query (a Python dict) for this dependency.

    OSV wants exactly this shape:
        {"package": {"ecosystem": "Maven", "name": "<group>:<artifact>"}, "version": "<version>"}

    Hints: dep.name gives "group:artifact", dep.version gives "2.14.1".
    Docs:  https://google.github.io/osv.dev/post-v1-querybatch/
    """
    raise NotImplementedError("TODO 1: build the OSV query for " + str(dep))


# --------------------------------------------------------------------------- MISSION 2
def severity_of(vuln):
    """
    TODO 2: Return the severity label of one OSV vulnerability record.

    GitHub advisories (ids starting with GHSA-) store it here:
        vuln["database_specific"]["severity"]   ->  "LOW" | "MODERATE" | "HIGH" | "CRITICAL"

    Some records don't have it - return "UNKNOWN" in that case (use .get()!).
    """
    raise NotImplementedError("TODO 2: read the severity")


# --------------------------------------------------------------------------- MISSION 3
def should_block(severity):
    """
    TODO 3: Return True if this severity is at FAIL_ON or worse.

    Hint: SEVERITY_ORDER.index("HIGH") is 3 and SEVERITY_ORDER.index("CRITICAL") is 4.
    """
    raise NotImplementedError("TODO 3: decide if this blocks the release")


# --------------------------------------------------------------------------- the gate
def main():
    pom = sys.argv[1] if len(sys.argv) > 1 else "pom.xml"
    deps = depreader.read_pom(pom)
    print(f"Scanning {len(deps)} dependencies...\n")

    queries = [build_query(d) for d in deps]
    results = post_json(OSV_BATCH_URL, {"queries": queries})["results"]

    blocking = 0
    for dep, result in zip(deps, results):
        vuln_ids = [v["id"] for v in result.get("vulns", [])]
        if not vuln_ids:
            print(f"  OK    {dep}")
            continue
        print(f"  VULN  {dep}  ({len(vuln_ids)} known issues)")
        for vid in vuln_ids[:3]:
            vuln = get_json(OSV_VULN_URL.format(id=vid))
            sev = severity_of(vuln)
            print(f"          {sev:<9} {vid}  {vuln.get('summary', '')[:70]}")
        for vid in vuln_ids:
            if should_block(severity_of(get_json(OSV_VULN_URL.format(id=vid)))):
                blocking += 1

    if blocking:
        print(f"\nGATE: BLOCKED ({blocking} issues at {FAIL_ON} or above)")
        sys.exit(1)       # <- a non-zero exit code is what stops a CI pipeline
    print("\nGATE: PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
