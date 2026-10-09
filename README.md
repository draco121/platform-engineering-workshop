# Platform Engineering Workshop: Guardrails & Golden Paths

A two-session, hands-on workshop for people meeting platform engineering for the first time.
You build the two things every platform team ships:

1. **A guardrail: a security gate** that blocks a release when it ships a library with a known
   vulnerability (using [OSV.dev](https://osv.dev)), running in GitHub Actions.
2. **A golden path: a service template** on GitHub. One click on **Use this template** gives you a
   personalised Spring Boot microservice whose pipeline already runs that security gate.

No prior security or DevOps experience needed.

> ⚠️ **`demo-app/` is vulnerable on purpose.** It pins old library versions (Log4Shell, Text4Shell and friends) so the gate has something to catch.
> It's harmless as a lab exercise, but never copy its versions into a real project. Expect GitHub security alerts on this repo,
> and a **red X on the Actions run**: the gate is blocking the demo app, which is the point. Lab 1 shows you how to make it green in your own fork.

## The two sessions

| Session | Topic | Lab | Where |
|---|---|---|---|
| 1 | What is platform engineering? Software vulnerabilities, and how to detect and fix them | [Lab 1 · Build a security gate](labs/LAB-1-security-gate.md) | this repo |
| 2 | Rapid microservice development with templates, and open problems | [Lab 2 · From one click to a green pipeline](labs/LAB-2-golden-path.md) | [java-service-template](https://github.com/draco121/java-service-template) |

## What's inside

| Path | What it is |
|---|---|
| `demo-app/` | **Old Faithful**, a tiny Java app with deliberately outdated, vulnerable dependencies |
| `gates/osv_gate.py` | The finished security gate |
| `gates/starter_osv_gate.py` | The Lab 1 starter with 3 TODOs |
| `labs/` | Mission sheets for both labs, answers folded under "Check your answer" |
| `.github/workflows/gates.yml` | Runs the security gate on the demo app on every push (red on purpose) |
| `.github/workflows/platform-gates.yml` | The *central* gate every service created from the template calls |
| `FACILITATOR.md` | Run sheets, hints and troubleshooting for whoever runs the workshop |

## Before the workshop (10 minutes)

```bash
python --version        # 3.9 or newer
java -version           # 17 or newer   (Lab 1 boss level, Lab 2)
mvn -v                  # 3.9 or newer
git --version
```

And create a free [GitHub](https://github.com) account if you don't have one.

## Quick start (Session 1)

```bash
git clone https://github.com/draco121/platform-engineering-workshop.git
cd platform-engineering-workshop/gates
python osv_gate.py ../demo-app/pom.xml        # -> GATE: BLOCKED
```

Then open [`labs/LAB-1-security-gate.md`](labs/LAB-1-security-gate.md) and start with `starter_osv_gate.py`.

## How the pieces fit

```
 Session 2                                         Session 1
 ─────────                                         ─────────
 java-service-template  ── "Use this template" ──▶  your-new-service
   (golden path)              + bootstrap Action      ci.yml: build + tests + formatting
                                                          │
                                                          ▼
                                    platform-gates.yml (central, in this repo)
                                          └─ osv_gate.py → BLOCK on HIGH/CRITICAL
                                                          │
                                                          ▼
                                                        deploy
```

The gate uses only the Python standard library, and OSV.dev is free with no API key.

> Vulnerability data changes daily. The numbers you see may differ from the slides. That's the lesson:
> a dependency that was safe last month can be blocked today.

## Ideas for going further

- Teach `depreader.py` to read `package.json` or `requirements.txt`, so the same gate works for Node.js or Python.
- Add a "new findings only" mode that blocks just the issues a pull request introduces.
- Build a Node.js or Python template repository.
- Try the production-grade tools: [OSV-Scanner](https://google.github.io/osv-scanner/), [Trivy](https://trivy.dev), [Backstage](https://backstage.io).

Pull requests welcome.
