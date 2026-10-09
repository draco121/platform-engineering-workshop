# Lab 2 - Build a License Gate (30 min, + 15 min CI challenge)

> **The story.** Your startup ships a closed-source invoicing app. An engineer added a
> handy PDF library two years ago. Today, during an investment deal, the lawyers find
> it is licensed **AGPL-3.0** - which can require you to publish your whole app's source
> code. The deal stalls.
>
> Nobody *wrote* a vulnerability. Nobody *broke* the build. It's a different kind of risk,
> and a gate can catch it too.

## Licenses in 60 seconds

| Family | Examples | What it means for a company shipping closed-source software | Typical verdict |
|---|---|---|---|
| **Permissive** | MIT, Apache-2.0, BSD | Use it, keep the copyright notice. That's it. | ALLOW |
| **Weak copyleft** | LGPL, MPL-2.0, EPL | OK to use; changes *to the library itself* must be shared | REVIEW |
| **Strong copyleft** | GPL-2.0, GPL-3.0 | Distributing it inside your app can oblige you to open your source | DENY |
| **Network copyleft** | AGPL-3.0 | Like GPL, and *running it as a web service* counts as distributing | DENY |
| **Unknown / odd** | "non-standard", missing | Nobody knows. A human must look | REVIEW |

License ids like `Apache-2.0` come from **SPDX** (https://spdx.org/licenses), a standard list.
Not legal advice: real companies have lawyers write the policy; the platform enforces it.

## Setup

```bash
cd platform-engineering-workshop/gates
python starter_license_gate.py ../demo-app/pom.xml
```

## Missions

Same rules as Lab 1: try first, then open "Check your answer", and raise your hand when your team clears a mission.

### Mission 2.1 - Read the label
Open https://deps.dev/maven/com.itextpdf%3Aitextpdf/5.5.13.3 in your browser.

**Checkpoint:** which SPDX license id does this version have?
<details><summary>Check your answer</summary>

`AGPL-3.0`.
</details>

### Mission 2.2 - Ask deps.dev
Solve **TODO 1** (`licenses_for`) in `starter_license_gate.py`. Tip: open this URL in your
browser first to see the JSON you're parsing:
https://api.deps.dev/v3/systems/maven/packages/org.yaml%3Asnakeyaml/versions/1.33

**Checkpoint:** the starter now crashes on TODO 2. What license does snakeyaml 1.33 have?
<details><summary>Check your answer</summary>

`Apache-2.0`.

```python
def licenses_for(dep):
    url = DEPS_DEV_URL.format(name=urllib.parse.quote(dep.name, safe=""), version=dep.version)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp).get("licenses") or ["UNKNOWN"]
```
</details>

### Mission 2.3 - Judge it
Solve **TODO 2** (`classify`). Run the starter.

**Checkpoint:** your gate prints `GATE: BLOCKED`. Which package does it DENY?
<details><summary>Check your answer</summary>

`itextpdf` (AGPL-3.0).

```python
def classify(license_id):
    if license_id in POLICY["ALLOW"]:
        return "ALLOW"
    if license_id in POLICY["DENY"]:
        return "DENY"
    return "REVIEW"
```
</details>

### Mission 2.4 - The fine print
Solve **TODO 3** (`classify_expression`) so that `"MIT OR GPL-2.0"` and `"MIT AND GPL-2.0"` work.
Test it in a Python shell: `python -c "import starter_license_gate as g; print(g.classify_expression('MIT OR GPL-2.0'))"`

**Checkpoint:** what is the verdict for `MIT OR GPL-2.0`? And for `MIT AND GPL-2.0`?
<details><summary>Check your answer</summary>

`ALLOW` (you may pick MIT) and `DENY` (you must obey both).

```python
def classify_expression(expr):
    if " OR " in expr:
        return min((classify_expression(p) for p in expr.split(" OR ")), key=RISK.index)
    if " AND " in expr:
        return max((classify_expression(p) for p in expr.split(" AND ")), key=RISK.index)
    return classify(expr.strip("() "))
```
</details>

### Mission 2.5 - Replace it
Swap iText for a PDF library from the Apache Software Foundation (Apache-2.0 licensed).
Search https://central.sonatype.com. Re-run `python license_gate.py ../demo-app/pom.xml`.

**Checkpoint:** no DENY lines left.
<details><summary>Check your answer</summary>

Apache PDFBox: `org.apache.pdfbox:pdfbox`. The demo code never calls iText, so only the pom changes.
</details>

### Mission 2.6 - Boss level: the mystery license
`mysql:mysql-connector-java` shows **non-standard**, and in Lab 1 it had an advisory with
*no fixed version*. Detective work: open its page on https://central.sonatype.com or
https://mvnrepository.com. The package didn't die - it **moved**.

**Checkpoint:** what are its new coordinates (`groupId:artifactId`)?
<details><summary>Check your answer</summary>

`com.mysql:mysql-connector-j`. Renamed packages break vulnerability tracking too: that's why
the old name had "no fixed version".
</details>

## The CI challenge: make GitHub say green (15 min)

This repository runs **both gates on GitHub Actions** on every push (`.github/workflows/gates.yml`).
On the original repo the run is red on purpose: Old Faithful is blocked. Your job is to turn it green.

1. Click **Fork** on https://github.com/draco121/platform-engineering-workshop (you need a free GitHub account).
2. In your fork, open the **Actions** tab and click the button to enable workflows.
3. Edit `demo-app/pom.xml` in your fork (on github.com: open the file, click the pencil icon) with
   the fixes from Missions 1.5, 2.5 and 2.6. Commit to `main`.
4. Watch the **Actions** tab. Both the security gate and the license gate run against the *full* dependency tree.

**Checkpoint:** a green check mark next to your commit. Click into the run to read the gate output,
and download the JSON reports from the run's **Artifacts** section.
<details><summary>Stuck?</summary>

Copy `demo-app/solution/pom.fixed.xml` over `demo-app/pom.xml`. If the security gate is still red,
a new advisory may have appeared since October 2026: the log tells you the version to upgrade to.
That is the lesson of this whole lab.
</details>

## Bonus round

1. Open `license-policy.json`. Find the `overrides` section. Why must every override carry evidence?
2. Run the full gate against the transitive tree (`--deps-file`, see Lab 1). Did anything new appear?
3. Debate with your neighbour: should the gate block on REVIEW (`--strict`)? Who pays if it does? Who pays if it doesn't?

## What the real tools add

FOSSA, Snyk, Black Duck, ORT (OSS Review Toolkit, open source) and others scan the actual license
*text* inside files (not just metadata), generate SBOMs (Software Bills of Materials) and the
"third-party notices" file you must ship, and route REVIEW cases to legal with an approval workflow.
