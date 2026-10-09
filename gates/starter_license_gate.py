#!/usr/bin/env python3
"""
LAB 2 STARTER - build your own license gate.

Run it:      python starter_license_gate.py ../demo-app/pom.xml
Stuck?       The finished version is license_gate.py in this folder.

There are 3 TODOs. Each one is a mission in labs/LAB-2-license-gate.md.
"""

import json
import sys
import urllib.parse
import urllib.request

import depreader

DEPS_DEV_URL = "https://api.deps.dev/v3/systems/maven/packages/{name}/versions/{version}"
RISK = ["ALLOW", "REVIEW", "DENY"]

# A tiny policy to start with. license-policy.json has the full company version.
POLICY = {
    "ALLOW": {"Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "EPL-2.0"},
    "DENY": {"GPL-2.0", "GPL-3.0", "AGPL-3.0"},
}


# --------------------------------------------------------------------------- MISSION 1
def licenses_for(dep):
    """
    TODO 1: Ask deps.dev for the licenses of this exact version.

    1. Build the URL with DEPS_DEV_URL.format(name=..., version=...)
       The name contains ":" so it must be URL-encoded:
           urllib.parse.quote(dep.name, safe="")   ->  "org.yaml%3Asnakeyaml"
    2. Download it (urllib.request.urlopen + json.load)
    3. Return the "licenses" list from the JSON, e.g. ["Apache-2.0"]

    Try it in the browser first:
    https://api.deps.dev/v3/systems/maven/packages/org.yaml%3Asnakeyaml/versions/1.33
    """
    raise NotImplementedError("TODO 1: fetch licenses for " + str(dep))


# --------------------------------------------------------------------------- MISSION 2
def classify(license_id):
    """
    TODO 2: Return "ALLOW", "DENY" or "REVIEW" for one license id.

    Rule of thumb used by most companies:
      - in POLICY["ALLOW"] -> "ALLOW"
      - in POLICY["DENY"]  -> "DENY"
      - anything else      -> "REVIEW"   (unknown = a human must look)
    """
    raise NotImplementedError("TODO 2: classify " + license_id)


# --------------------------------------------------------------------------- MISSION 3
def classify_expression(expr):
    """
    TODO 3 (bonus): Handle SPDX expressions like "MIT OR GPL-2.0".

      "A OR B"  -> you may pick either  -> the FRIENDLIEST verdict wins
      "A AND B" -> you must obey both   -> the STRICTEST verdict wins

    Hint: min(verdicts, key=RISK.index) gives the friendliest one.
    Until you solve it, this just calls classify().
    """
    return classify(expr)


# --------------------------------------------------------------------------- the gate
def main():
    pom = sys.argv[1] if len(sys.argv) > 1 else "pom.xml"
    deps = depreader.read_pom(pom)
    print(f"Checking licenses of {len(deps)} dependencies...\n")

    denied = 0
    for dep in deps:
        lics = licenses_for(dep)
        verdict = max((classify_expression(l) for l in lics), key=RISK.index)
        denied += verdict == "DENY"
        print(f"  {verdict:<7} {str(dep):<55} {', '.join(lics)}")

    if denied:
        print(f"\nGATE: BLOCKED ({denied} package(s) with a denied license)")
        sys.exit(1)
    print("\nGATE: PASSED")


if __name__ == "__main__":
    main()
