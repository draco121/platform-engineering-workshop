# Facilitator Guide

How to run *Guardrails & Golden Paths* with this repository. Everything the room needs is here:
the demo app, the two gates, the template, the lab sheets and a GitHub Actions run of both gates.
The three slide decks follow the same structure; every slide has speaker notes.

---

## 1. The shape of the workshop

| | Session 1 (~2.5 h) | Session 2 (~2 h) |
|---|---|---|
| Deck | Part 1 · What is Platform Engineering? → Part 2 · Security & License Gates | Part 3 · Golden Paths & Open Problems |
| Labs | Lab 1 (security gate), Lab 2 (license gate + CI challenge) | Lab 3 (Cookiecutter template) |
| Code | `demo-app/`, `gates/` | `templates/java-service/` |

### Session 1 run sheet

| Time | What | Room interaction |
|---|---|---|
| 0:00 | Part 1, slides 1–3 | Everyone opens the repo link on the "today" slide; teams of 2–3 form |
| 0:10 | Slides 4–13 (QuickBite story, definition, gates) | "If you were the CTO…" question on the chaos slide |
| 0:30 | Slides 14–15 "Platform or not?" quiz | Four corners or hands up per option; neighbours argue for 60 s first |
| 0:35 | Slide 16 ready check: everyone clones and runs `osv_gate.py` | Hands up when you see `GATE: BLOCKED` |
| 0:40 | Break (5 min) | |
| 0:45 | Part 2, slides 1–9 incl. live demo | Hands up for "where should the gate block?" on the severity slide |
| 1:05 | Slides 10–11, Lab 1 brief | |
| 1:10 | **Lab 1** (40 min) | Raise hands at each checkpoint; first team to clear 1.6 shows their screen |
| 1:50 | Slides 12–18 (tools, licenses) | |
| 2:05 | **Lab 2** (30 min) + CI challenge (15 min) | First green check mark on a fork goes on the projector |
| 2:50 | Slides 21–22 (central gates, recap) | |

### Session 2 run sheet

| Time | What | Room interaction |
|---|---|---|
| 0:00 | Part 3, slides 1–13 | "What do you do before writing the first line of Coupons?" shout-out on slide 2 |
| 0:25 | **Lab 3** (45 min) | Raise hands at each checkpoint; check 3.6 builds in person |
| 1:10 | Slides 15–20 (drift, open problems) | After each pair of problems: "which would you work on?" by hands |
| 1:35 | Slides 21–22 (resources, wrap-up) | Star / fork the repo; feedback (section 4) |

---

## 2. Before the workshop

**A week before**
- [ ] Share the repo link and ask students to do the "Before the workshop" steps in `README.md`.
- [ ] Fill in the bracketed placeholders in the decks (your name, contact).
- [ ] Optional: turn on **Discussions** in the repo settings, for questions and feedback (section 4).

**The day before** (vulnerability data changes daily, so re-run these)
```bash
cd gates
python osv_gate.py ../demo-app/pom.xml        # should say BLOCKED
python license_gate.py ../demo-app/pom.xml    # should say BLOCKED
cd ../templates && cookiecutter --no-input java-service && cd order-service && mvn -q verify
```
Also check that the latest **Actions** run on the repo is red (it should be: the demo app is blocked).
If the numbers differ from the slides (e.g. "69 issues"), say so in the room: it proves that new
advisories arrive all the time.

**On the day**
- [ ] Phone hotspot as a Wi-Fi backup. The gates need api.osv.dev and api.deps.dev; Lab 3 needs Maven Central.
- [ ] A terminal open in `gates/` for the live demos, and the repo's **Actions** tab in a browser tab.
- [ ] A whiteboard corner for team names and checkpoints cleared, if you want a light competition.

---

## 3. Engagement without extra tools

- **Teams of 2–3.** Pairing halves setup problems and doubles the talking.
- **Checkpoints, not flags.** Every mission ends with something visible on screen. Teams raise a hand;
  you glance, nod, tick their row on the whiteboard.
- **Screen of fame.** The first team to clear each boss level (1.6, 2.6, 3.5) plugs into the projector
  and explains how they found it. Two minutes, big applause.
- **Votes by hands or four corners.** Quiz options A–D map to the four corners of the room.
- **The CI challenge (Lab 2).** Students fork the repo, fix `demo-app/pom.xml` on github.com and
  watch both gates turn green in GitHub Actions. It connects the labs to how real pipelines work,
  and the green check mark is a satisfying moment to put on the projector.
- **Hints out loud.** When several teams are stuck on the same mission, pause the room and give the
  hint once (section 5).
- **Answers are in the lab sheets**, folded under "Check your answer". Ask teams to try first; it's
  a learning workshop, not an exam.

## 4. Questions and feedback on GitHub

If you enable **Discussions** on the repo, create two threads before the session:
"Questions during the workshop" and "Feedback". Put the link on your last slide. Students can keep
asking after the session, and you keep everything in one place. Without Discussions, a GitHub issue
titled "Workshop feedback" works the same way.

---

## 5. Ready-made hints

- **1.2** `dep.name` already gives you "group:artifact" with the colon. The ecosystem is spelled `Maven`.
- **1.3** Use `vuln.get("database_specific", {}).get("severity", "UNKNOWN")`.
- **1.4** `SEVERITY_ORDER.index(severity) >= SEVERITY_ORDER.index(FAIL_ON)`
- **1.6** Run `mvn dependency:tree` in demo-app to see who brings in what.
- **2.2** The ":" in the package name must be URL-encoded: `urllib.parse.quote(dep.name, safe="")`.
- **2.4** OR = friendliest wins: `min(verdicts, key=RISK.index)`. AND = strictest: `max(...)`.
- **2.6** Open the old artifact on central.sonatype.com or mvnrepository.com and look for "relocated" / "moved".
- **CI challenge** Actions are off by default on forks: Actions tab → enable workflows. Then any commit triggers a run.
- **3.2** It's the same in every service, and it comes from OpenTelemetry.
- **3.5** Generate a NEW service after editing the template; existing ones keep their pom.

---

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| `urlopen error` / timeouts in the gates | Network. Switch to the hotspot; pair the team with a neighbour. |
| Windows: `python` not found | Use `py` instead of `python`. |
| Windows: exit code | `echo %ERRORLEVEL%` (cmd) or `$LASTEXITCODE` (PowerShell). |
| Fork's Actions tab shows nothing | Actions are disabled on new forks until enabled; then push a commit. |
| CI security gate still red with the solution pom | A new advisory was published. The log prints the version to upgrade to. |
| `cookiecutter: command not found` | `pip install cookiecutter`, or `python -m cookiecutter java-service`. |
| Lab 3 `mvn verify` fails on formatting after editing | That's Mission 3.3: `mvn spotless:apply`. |
| Port 8080 already in use | `mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=8081` |
| Java version errors in Lab 3 | Spring Boot 4 needs Java 17+. Re-generate with `java_version=17` if needed. |
