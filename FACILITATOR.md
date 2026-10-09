# Facilitator Guide

How to run *Guardrails & Golden Paths* as two sessions. Everything the room needs lives on GitHub:

- **This repo** (Session 1): the demo app, the security gate, both lab sheets, and the central gate workflow.
- **[java-service-template](https://github.com/draco121/java-service-template)** (Session 2): the golden-path template repository.

Each session has one slide deck with speaker notes on every slide.

---

## 1. Run sheets

### Session 1 · Platform engineering + security gate (~2.5 h)

| Time | What | Room interaction |
|---|---|---|
| 0:00 | Opening: agenda, poll, QuickBite story | Everyone opens the repo link; teams of 2–3 form |
| 0:10 | What platform engineering is, gates | "If you were the CTO…" on the chaos slide |
| 0:30 | "Platform or not?" quiz | Stand / sit per option; neighbours argue for 60 s first |
| 0:35 | Dependencies, CVEs, severity, OSV | Hands up for "where should the gate block?" |
| 0:55 | How the gate works, live demo, fixes | Everyone runs `osv_gate.py` and raises a hand at `GATE: BLOCKED` |
| 1:10 | Break (5 min) | |
| 1:15 | **Lab 1** (40 min) | Raise hands at each checkpoint; first team to clear 1.6 / 1.7 shows their screen |
| 1:55 | **CI challenge** (15 min) | First green check mark on a fork goes on the projector |
| 2:10 | Tools at scale, central gates, recap | Teaser: "who sets this up for a brand-new service?" |

### Session 2 · Golden paths with GitHub templates (~2 h)

| Time | What | Room interaction |
|---|---|---|
| 0:00 | The problem: 80 pieces of plumbing | "What do you do before writing the first line of Coupons?" |
| 0:15 | Golden paths, Cookiecutter, GitHub template repos | |
| 0:30 | **Live demo**: Use this template → bootstrap → green CI | Students guess the service name before the bot commits it |
| 0:40 | **Lab 2** (45 min) | Raise hands at each checkpoint; first team red-then-green on 2.6 shows their screen |
| 1:25 | Template drift, open problems | After each pair of problems: "which would you work on?" |
| 1:50 | Resources, wrap-up | Star / fork the repos; feedback in Discussions |

---

## 2. Before the workshop

**A week before**
- [ ] Share this repo's link and ask students to do the "Before the workshop" steps in `README.md`.
- [ ] Confirm `java-service-template` is marked as a template (**Settings → General → Template repository**).
- [ ] Do one dry run of Lab 2 yourself: Use this template → watch bootstrap and ci go green. Delete the test repo after.
- [ ] Fill in the bracketed placeholders in the decks (your name, contact).
- [ ] Optional: turn on **Discussions** in this repo for questions and feedback.

**The day before** (vulnerability data changes daily)
```bash
cd gates && python osv_gate.py ../demo-app/pom.xml        # should say BLOCKED
```
Check that this repo's latest **Actions** run is red, and that a fresh repo from the template still goes
green. If the numbers differ from the slides (e.g. "69 issues"), say so in the room: new advisories
arrive all the time, which is the point.

**On the day**
- [ ] Phone hotspot as a Wi-Fi backup (api.osv.dev, github.com, Maven Central).
- [ ] Browser tabs: this repo's Actions tab, the template repo, a terminal in `gates/`.
- [ ] A whiteboard corner for team names and checkpoints cleared, if you want a light competition.

---

## 3. Engagement without extra tools

- **Teams of 2–3.** Pairing halves setup problems and doubles the talking.
- **Checkpoints, not flags.** Every mission ends with something visible on screen. Teams raise a hand;
  you glance, nod, tick their row on the whiteboard.
- **Screen of fame.** The first team to clear each boss level (1.6, 1.7, 2.6) plugs into the projector
  and explains how they found it. Two minutes, big applause.
- **Live moments on GitHub.** The CI challenge (a fork going green) and Lab 2's bootstrap (a bot committing
  a service named after *your* repo) are the two "wow" moments. Put them on the projector.
- **Answers are in the lab sheets**, folded under "Check your answer". Ask teams to try first.
- **Questions and feedback** in this repo's Discussions (or a "Workshop feedback" issue), linked on the last slide.

---

## 4. Ready-made hints

- **1.2** `dep.name` already gives you "group:artifact" with the colon. The ecosystem is spelled `Maven`.
- **1.3** Use `vuln.get("database_specific", {}).get("severity", "UNKNOWN")`.
- **1.4** `SEVERITY_ORDER.index(severity) >= SEVERITY_ORDER.index(FAIL_ON)`
- **1.6** Run `mvn dependency:tree` in demo-app to see who brings in what.
- **1.7** Open the old artifact on central.sonatype.com or mvnrepository.com and look for "relocated" / "moved".
- **CI challenge** Actions are off by default on forks: Actions tab → enable workflows. Then any commit triggers a run.
- **2.1** Bootstrap takes about a minute. Refresh the code page after it goes green.
- **2.4** It's the same in every service, and it comes from OpenTelemetry.
- **2.6** Edit `pom.xml` on github.com with the pencil icon; no local setup needed.

---

## 5. Troubleshooting

| Symptom | Fix |
|---|---|
| `urlopen error` / timeouts in the gate | Network. Switch to the hotspot; pair the team with a neighbour. |
| Windows: `python` not found | Use `py` instead of `python`. |
| Windows: exit code | `echo %ERRORLEVEL%` (cmd) or `$LASTEXITCODE` (PowerShell). |
| Fork's Actions tab shows nothing | Actions are disabled on new forks until enabled; then push a commit. |
| CI still red with the solution pom | A new advisory was published. The log prints the version to upgrade to. |
| Lab 2: bootstrap didn't run | The repo was created with "Include all branches", or Actions are disabled in the account. Actions tab → **bootstrap** → **Run workflow**. |
| Lab 2: bootstrap failed at "push" | Account-level setting limits workflow permissions. Repo **Settings → Actions → General → Workflow permissions → Read and write**, then re-run. |
| Lab 2: ci security gate red on a fresh repo | A new advisory hit Spring Boot's libraries. Patch the version in the template repo's pom (like the existing PLATFORM SECURITY PATCHES) and tell the room: this is the platform team's job. |
| `mvn verify` fails on formatting | That's Mission 2.5: `mvn spotless:apply`. |
| Port 8080 already in use | `mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=8081` |
| Java version errors | Spring Boot 4 needs Java 17+. |
