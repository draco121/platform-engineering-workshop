# Lab 1 - Build a Security Gate (40 min + 15 min CI challenge)

> **The story.** It's December 2021. A logging library used by millions of Java apps,
> `log4j-core`, turns out to let attackers run code on your server by sending one
> specially crafted string ("Log4Shell"). Companies spent weeks just answering one
> question: *"Do we use it, and where?"*
>
> Today you'll build the robot that answers that question in 3 seconds - and refuses to
> ship the release until it's fixed.

## What you need

- Python 3.9+ (`python --version`). No pip installs.
- Internet access (we call the free OSV.dev API).
- Optional: Java 17+ and Maven, for the boss level.

```bash
git clone https://github.com/draco121/platform-engineering-workshop.git
cd platform-engineering-workshop/gates
python starter_osv_gate.py ../demo-app/pom.xml
```

You'll get a `NotImplementedError: TODO 1`. That's expected - that's your first mission.

## Words you'll meet

| Word | Plain English |
|---|---|
| **Dependency** | A library your code uses, listed in `pom.xml` |
| **Transitive dependency** | A library *your libraries* use. You never wrote it down, but you ship it |
| **Vulnerability / CVE** | A known security bug with a public id, e.g. `CVE-2021-44228` |
| **Advisory (GHSA)** | GitHub's write-up of a vulnerability, e.g. `GHSA-jfh8-c2jp-5v3q` |
| **OSV.dev** | Google's free, open database that combines advisories from many sources |
| **Gate** | A pipeline step that says PASS (exit 0) or BLOCK (exit 1) |

## Missions

Work in teams of 2-3. Each mission ends with a **checkpoint**: something you should see on your
screen or be able to answer. Try first, then open "Check your answer". When your team clears a
mission, raise your hand: the first team to clear the boss level shows their screen on the projector.

### Mission 1.1 - Recon
Open https://osv.dev and search for `log4j-core`. Find the advisory titled *Remote code injection in Log4j*.

**Checkpoint:** what is its CVE id?
<details><summary>Check your answer</summary>

`CVE-2021-44228`, the famous Log4Shell.
</details>

### Mission 1.2 - Ask the database
Open `starter_osv_gate.py` and solve **TODO 1** (`build_query`). Run the starter again.
You'll now crash on TODO 2 - but the request to OSV worked. Open this in a browser tab to see what one
full vulnerability record looks like: https://api.osv.dev/v1/vulns/GHSA-jfh8-c2jp-5v3q

**Checkpoint:** the crash message now mentions TODO 2, not TODO 1.
<details><summary>Check your answer</summary>

```python
def build_query(dep):
    return {"package": {"ecosystem": "Maven", "name": dep.name}, "version": dep.version}
```
</details>

### Mission 1.3 - How bad is it?
Solve **TODO 2** (`severity_of`). Run again: you now see severities.

**Checkpoint:** what severity does your gate print for `GHSA-mjmj-j48q-9wg2` (the SnakeYAML issue)?
<details><summary>Check your answer</summary>

`HIGH`. A working solution:

```python
def severity_of(vuln):
    return (vuln.get("database_specific") or {}).get("severity", "UNKNOWN")
```
</details>

### Mission 1.4 - Close the gate
Solve **TODO 3** (`should_block`). Run it, then run `echo $?` (macOS/Linux), `echo %ERRORLEVEL%` (Windows cmd)
or `$LASTEXITCODE` (PowerShell).

**Checkpoint:** your gate prints `GATE: BLOCKED`, and the exit code is not 0.
<details><summary>Check your answer</summary>

The exit code is `1`.

```python
def should_block(severity):
    return SEVERITY_ORDER.index(severity) >= SEVERITY_ORDER.index(FAIL_ON)
```
</details>

> Why the exit code matters: CI systems (GitHub Actions, Jenkins, GitLab) stop the pipeline
> when a step exits non-zero. That one number turns your script into a real deployment gate.

### Mission 1.5 - Fix it
Now run the full version: `python osv_gate.py ../demo-app/pom.xml`. It tells you which version
fixes each package. Edit `../demo-app/pom.xml` and upgrade the libraries.

**Checkpoint:** what is the *smallest* commons-text version that fixes Text4Shell (CVE-2022-42889)?
Keep upgrading until everything you can fix is green.
<details><summary>Check your answer</summary>

`1.10.0`. One package will refuse to turn green whatever version you try: that's Mission 1.7.
A pom that passes the gate (as of October 2026) is in `demo-app/solution/pom.fixed.xml`.
</details>

### Mission 1.6 - Boss level: the hidden ones
Your `pom.xml` lists 6 libraries. But Maven downloads more. Find out what you *really* ship:

```bash
cd ../demo-app
mvn -q dependency:list -DoutputFile=deps.txt -DincludeScope=runtime
cd ../gates
python osv_gate.py --deps-file ../demo-app/deps.txt
```

Some vulnerable packages are not in your pom at all. One of them is pulled in by the MySQL driver
(`mvn dependency:tree` in `demo-app` shows who brings in what).

**Checkpoint:** what is that package's artifactId?
<details><summary>Check your answer</summary>

`protobuf-java`.
</details>

### Mission 1.7 - Boss level: the package that moved
`mysql:mysql-connector-java` has a HIGH advisory, but the gate says
*"no fixed version published"*. No upgrade will ever fix it under this name. Why?
Detective work: open its page on https://central.sonatype.com or https://mvnrepository.com.
The package didn't die - it **moved**.

**Checkpoint:** what are its new coordinates (`groupId:artifactId`)? Put them in your pom and the
last red line disappears.
<details><summary>Check your answer</summary>

`com.mysql:mysql-connector-j`. Maven calls this a *relocation*. Renamed packages are a real headache
for security tooling: the old name stays vulnerable forever, and nobody upgrades it.
</details>

## The CI challenge: make GitHub say green (15 min)

This repository runs the **security gate on GitHub Actions** on every push (`.github/workflows/gates.yml`).
On the original repo the run is red on purpose: Old Faithful is blocked. Your job is to turn it green.

1. Click **Fork** on https://github.com/draco121/platform-engineering-workshop (you need a free GitHub account).
2. In your fork, open the **Actions** tab and click the button to enable workflows.
3. Edit `demo-app/pom.xml` in your fork (on github.com: open the file, click the pencil icon) with
   your fixes from Missions 1.5 and 1.7. Commit to `main`.
4. Watch the **Actions** tab. The gate runs against the *full* dependency tree, hidden libraries included.

**Checkpoint:** a green check mark next to your commit. Click into the run to read the gate output,
and download the JSON report from the run's **Artifacts** section.
<details><summary>Stuck?</summary>

Copy `demo-app/solution/pom.fixed.xml` over `demo-app/pom.xml`. If the gate is still red,
a new advisory may have appeared since October 2026: the log tells you the version to upgrade to.
That is the lesson of this whole lab.
</details>

## Bonus round

1. **Accepted risk.** Create `.osv-ignore.json` with one entry, a reason and an `expires` date:
   `[{"id": "GHSA-mjmj-j48q-9wg2", "reason": "not reachable, see ticket SEC-12", "expires": "2026-12-31"}]`.
   Run the gate again. Why must every exception expire?
2. **Tune the gate.** Run with `--fail-on CRITICAL`. What gets through now? Who should decide this number?
3. **Compare with the pros.** Install [osv-scanner](https://google.github.io/osv-scanner/) or
   [Trivy](https://trivy.dev) and scan the same folder. What do they find that yours doesn't?

## What the real tools add

Your ~250 lines do the core job. Commercial and open-source scanners (Snyk, Trivy, osv-scanner,
GitHub Dependabot, Palo Alto's Cortex Cloud - formerly Prisma Cloud) add: container-image and
OS-package scanning, "is the vulnerable code actually reachable?" analysis, automatic fix pull
requests, dashboards across hundreds of repos, and policy management.
