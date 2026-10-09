# Platform Engineering Workshop: Guardrails & Golden Paths

A hands-on lab kit for learning platform engineering by building three things yourself:

1. **A security gate** that blocks a release when it ships a library with a known vulnerability (using [OSV.dev](https://osv.dev)).
2. **A license gate** that blocks libraries whose license your company can't accept (using [deps.dev](https://deps.dev)).
3. **A golden-path template** that creates a production-ready Spring Boot microservice in one command (using [Cookiecutter](https://github.com/cookiecutter/cookiecutter)).

Written for people meeting these ideas for the first time. No prior security or DevOps experience needed.

> ⚠️ **`demo-app/` is vulnerable on purpose.** It pins old library versions (Log4Shell, Text4Shell and friends) so the gates have something to catch.
> It's harmless as a lab exercise, but never copy its versions into a real project. Expect GitHub security alerts on this repo,
> and a **red X on the Actions run**: the gates are blocking the demo app, which is the point. Lab 2 shows you how to make it green in your own fork.

## What's inside

| Folder | What it is | Used in |
|---|---|---|
| `demo-app/` | **Old Faithful**, a tiny Java app with deliberately outdated, risky dependencies | Labs 1 + 2 |
| `gates/` | The security gate, the license gate, starter files with TODOs, and the license policy | Labs 1 + 2 |
| `templates/java-service/` | A Cookiecutter golden-path template for a Spring Boot 4 microservice | Lab 3 |
| `labs/` | Step-by-step mission sheets for each lab | All |
| `.github/workflows/gates.yml` | Runs both gates on the demo app on every push (red on purpose) | Lab 2 CI challenge |
| `.github/workflows/platform-gates.yml` | The *central* reusable CI workflow every generated service calls | Lab 3 |
| `FACILITATOR.md` | Run sheets, hints and troubleshooting for whoever runs the workshop | - |

## Before the workshop (10 minutes)

```bash
python --version        # 3.9 or newer
java -version           # 17 or newer   (Lab 3 and the Lab 1 boss level)
mvn -v                  # 3.9 or newer
pip install cookiecutter

git clone https://github.com/draco121/platform-engineering-workshop.git
cd platform-engineering-workshop

# Warm up Maven's cache so the venue Wi-Fi doesn't have to:
cd demo-app && mvn -q dependency:resolve && cd ..
cd templates && cookiecutter --no-input java-service && cd order-service && mvn -q verify && cd ../..
```

If all of that ran without errors, you're ready.

## Quick start

```bash
cd gates
python osv_gate.py ../demo-app/pom.xml        # security gate  -> BLOCKED
python license_gate.py ../demo-app/pom.xml    # license gate   -> BLOCKED
```

Then open [`labs/LAB-1-security-gate.md`](labs/LAB-1-security-gate.md) and start with the starter files.

| Lab | Time | You build |
|---|---|---|
| [Lab 1](labs/LAB-1-security-gate.md) | 40 min | `gates/starter_osv_gate.py` → a working security gate |
| [Lab 2](labs/LAB-2-license-gate.md) | 45 min | `gates/starter_license_gate.py` → a working license gate, then both gates green on GitHub Actions in your fork |
| [Lab 3](labs/LAB-3-golden-path.md) | 45 min | Your own microservice from the golden-path template |

Every mission ends with a checkpoint, and the answers are folded under "Check your answer" in the lab sheets.
Stuck? The finished versions are `gates/osv_gate.py` and `gates/license_gate.py`. Try not to peek too early.

## How the pieces fit

```
 developer runs:  cookiecutter java-service          (golden path, Lab 3)
        |
        v
 new service repo  --push-->  ci.yml: build + test + formatting
                                  |
                                  v
                      platform-gates.yml (central, owned by the platform team)
                         |-- osv_gate.py      -> BLOCK on HIGH/CRITICAL vulnerabilities  (Lab 1)
                         `-- license_gate.py  -> BLOCK on denied licenses               (Lab 2)
                                  |
                                  v
                               deploy
```

The gates use only the Python standard library, and both data sources are free with no API key.

> Vulnerability data changes daily. The numbers you see may differ from the slides. That's the lesson:
> a dependency that was safe last month can be blocked today.

## Ideas for going further

- Teach `depreader.py` to read `package.json` or `requirements.txt`, so the same gates work for Node.js or Python.
- Add a "new findings only" mode that blocks just the issues a pull request introduces.
- Build a Node.js or Python golden-path template.
- Try the production-grade tools: [OSV-Scanner](https://google.github.io/osv-scanner/), [Trivy](https://trivy.dev), [Backstage](https://backstage.io).

Pull requests welcome.
