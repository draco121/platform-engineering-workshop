# Lab 2 - From One Click to a Green Pipeline (45 min)

> **The story.** Your company has 10 microservices, built by 4 teams. Each team wrote its own
> logging, its own health checks, its own Dockerfile, its own CI. When a customer reports
> "checkout is slow", nobody can follow the request across services, because every service
> logs differently. The security team needs a patch in all 10 - that's 10 pull requests,
> 4 code styles, 2 weeks.
>
> The platform fix: a **golden path template**. One click, and a new service starts with every
> cross-cutting concern already done - the same way, everywhere - and the security gate you
> built in Lab 1 already guarding its pipeline.

## What you need

- A free GitHub account. Missions 2.1, 2.2 and 2.6 work entirely in the browser.
- For 2.3–2.5: `git`, Java 17+ and Maven 3.9+ (`mvn -v`), and `curl` (or a browser).

## Words you'll meet

| Word | Plain English |
|---|---|
| **Microservice** | A small app that does one job and talks to others over HTTP |
| **Cross-cutting concern** | Something *every* service needs that isn't the business feature: logs, metrics, tracing, health, security, CI |
| **Golden path** | The paved, supported, recommended way to build something in your org |
| **Template repository** | A GitHub repo with a **Use this template** button: it copies all its files into a brand-new repo |
| **Cookiecutter** | An open-source tool that fills in the blanks (`{{ service_name }}`) in a project template |
| **Bootstrap** | The one-time GitHub Action that runs Cookiecutter in your new repo, using the repo's name |

## Missions

Same rules as Lab 1: try first, then open "Check your answer", and raise your hand when your team clears a mission.

### Mission 2.1 - One click
1. Open https://github.com/draco121/java-service-template and look around: `template/` holds the
   Cookiecutter template, `.github/workflows/` holds two workflows.
2. Click **Use this template → Create a new repository**. Name it after a service, for example
   `coupon-service` (any name works). Click **Create repository**.
3. In your new repository, open the **Actions** tab. A workflow called **bootstrap** is running.

**Checkpoint:** when bootstrap finishes, refresh the code page. The `template/` folder is gone, there's a
`pom.xml`, and the README's title is your service's name.
<details><summary>Check your answer</summary>

For a repo named `coupon-service` you get `# Coupon Service`, artifactId `coupon-service` and Java
package `dev.workshop.couponservice`. Look at the commit history: the second commit,
*"Bootstrap Coupon Service from java-service-template"*, was made by the bot, not by you.
</details>

### Mission 2.2 - Born green
Back in the **Actions** tab, a second workflow called **ci** started on its own after bootstrap.
Click into it.

**Checkpoint:** the run is green. Which jobs ran, and where does the security gate's code come from?
<details><summary>Check your answer</summary>

Three jobs: *Is there a service to build?*, *Build, test, check formatting* and
*Platform / Security gate (OSV.dev)*. The security gate isn't in your repo: your `ci.yml` calls the
platform team's central workflow in `draco121/platform-engineering-workshop`. It ran the same
`osv_gate.py` you built in Lab 1, against about 90 libraries your service ships.
</details>

### Mission 2.3 - Run it

```bash
git clone https://github.com/<your-user>/<your-repo>.git
cd <your-repo>
mvn spring-boot:run
# in a second terminal:
curl -i "localhost:8080/api/greeting?name=you"
curl -i "localhost:8080/api/greeting?name=%20"
```

**Checkpoint:** which response header carries a unique id for your request? And what comes back
for the blank name?
<details><summary>Check your answer</summary>

`X-Request-Id`, added by `platform/RequestIdFilter.java`, which the template wrote for you.
The blank name returns `400` with a clean JSON error ("Problem Details", RFC 9457), never a stack trace.
</details>

### Mission 2.4 - Follow the request
Look at the terminal where your service is running. Every log line is JSON.
One field is shared by *all* log lines of one request, across *all* services it touches
(it comes from OpenTelemetry tracing).

**Checkpoint:** what is that field called?
<details><summary>Check your answer</summary>

`traceId`. (`requestId` is there too, but it's created by this service; `traceId` travels with the
request to every service it calls.)
</details>

### Mission 2.5 - Robots don't argue about style
Open any `.java` file, make one line very long or mess up the indentation, then commit and push.
Watch **ci** in the Actions tab.

**Checkpoint:** the build job goes red. Read its log: what command fixes formatting automatically?
Run it locally, push again, and get back to green.
<details><summary>Check your answer</summary>

`mvn spotless:apply`. The same check runs on your laptop (`mvn verify`) and in CI, so style
arguments never reach code review.
</details>

### Mission 2.6 - Boss level: be the platform team
Open `pom.xml` in your repository (on github.com, the pencil icon works) and find
**PLATFORM SECURITY PATCHES**. Delete the two version lines and commit.

**Checkpoint:** the build passes, but the security gate goes red. Which embedded web server
package does it block? Put the lines back and you're green again.
<details><summary>Check your answer</summary>

`tomcat-embed-core`: Spring Boot 4.1.1 ships Tomcat 11.0.24, which has CRITICAL advisories. The
platform team pinned a patched version in the template, so every new service is born green.
If nothing is blocked when you try this, a newer Spring Boot release may already include the fix.

Discussion: the patch lives in *your* pom now. When the next Tomcat advisory appears, how do the
50 services already created from the template get the fix? (Hint: they don't, automatically.
Look up "template drift".)
</details>

## Bonus round

1. **The command-line path.** Same template, no GitHub button:
   `pip install cookiecutter && cookiecutter gh:draco121/java-service-template --directory template`
2. **Extend the golden path.** Fork `java-service-template`, add a question to
   `template/cookiecutter.json` (for example `"include_database": ["no", "yes"]`) and use it in
   `pom.xml` with `{% if cookiecutter.include_database == "yes" %} ... {% endif %}`.
   In your fork, tick **Settings → General → Template repository**, then use *your* template.
3. **Discuss with your neighbour.** A team wants Go instead of Java. Should the platform say no,
   or offer a second template? What should **never** be in a template?
