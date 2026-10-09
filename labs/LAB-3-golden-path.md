# Lab 3 - Ship a Production-Ready Microservice in 5 Minutes (45 min)

> **The story.** Your company has 10 microservices, built by 4 teams. Each team wrote its own
> logging, its own health checks, its own Dockerfile, its own CI. When a customer reports
> "checkout is slow", nobody can follow the request across services, because every service
> logs differently. The security team needs a patch in all 10 - that's 10 pull requests,
> 4 code styles, 2 weeks.
>
> The platform fix: a **golden path template**. One command, and a new service starts with
> every cross-cutting concern already done - the same way, everywhere.

## What you need

- Python 3.9+ and `pip install cookiecutter`
- Java 17+ and Maven 3.9+ (`mvn -v`)
- `curl` (or a browser)

## Words you'll meet

| Word | Plain English |
|---|---|
| **Microservice** | A small app that does one job and talks to others over HTTP |
| **Cross-cutting concern** | Something *every* service needs that isn't the business feature: logs, metrics, tracing, health, security, CI |
| **Boilerplate** | Code you copy-paste to get started that has nothing to do with your feature |
| **Template / scaffold** | A project skeleton with blanks (`{{ service_name }}`) that a tool fills in |
| **Golden path** | The paved, supported, recommended way to build something in your org |
| **Cookiecutter** | A popular open-source tool that turns a template folder into a real project |

## Missions

Same rules as Labs 1 and 2: try first, then open "Check your answer", and raise your hand when your team clears a mission.

### Mission 3.1 - Generate

```bash
cd platform-engineering-workshop/templates
cookiecutter java-service
```

Answer the questions (use your own service name!). Then:

```bash
cd <your-service-slug>
mvn spring-boot:run
# in a second terminal:
curl -i "localhost:8080/api/greeting?name=you"
```

**Checkpoint:** which response header carries a unique id for your request?
<details><summary>Check your answer</summary>

`X-Request-Id`. It comes from `platform/RequestIdFilter.java`, which the template wrote for you.
</details>

### Mission 3.2 - Follow the request
Look at the terminal where your service is running. Every log line is JSON.
One field is shared by *all* log lines of one request, across *all* services it touches
(it comes from OpenTelemetry tracing).

**Checkpoint:** what is that field called?
<details><summary>Check your answer</summary>

`traceId`. (`requestId` is there too, but it's created by this service; `traceId` travels with the
request to every service it calls.)
</details>

### Mission 3.3 - Robots don't argue about style
Open any `.java` file and make a line very long, or mess up the indentation. Run `mvn verify`.
It fails. Read the error message.

**Checkpoint:** what exact Maven command fixes formatting automatically?
<details><summary>Check your answer</summary>

`mvn spotless:apply`
</details>

### Mission 3.4 - Guardrails, not gates-in-your-face
Call your API with a blank name: `curl -i "localhost:8080/api/greeting?name=%20"`
You get a clean JSON error, not a Java stack trace. The template did that.

**Checkpoint:** what HTTP status code comes back?
<details><summary>Check your answer</summary>

`400` (Bad Request), as RFC 9457 "Problem Details" JSON.
</details>

### Mission 3.5 - Be the platform team
Open `templates/java-service/{{cookiecutter.service_slug}}/pom.xml` and find **PLATFORM SECURITY
PATCHES**. Comment out the two version lines. Generate a fresh service, then run the security
gate from Lab 1 on it:

```bash
cd <new-service>
mvn -q dependency:list -DoutputFile=deps.txt -DincludeScope=runtime
python ../../gates/osv_gate.py --deps-file deps.txt
```

The newest Spring Boot release is blocked. Put the lines back - one edit, and every new
service is fixed.

**Checkpoint:** which embedded web server package is blocked?
<details><summary>Check your answer</summary>

`tomcat-embed-core` (Spring Boot 4.1.1 ships Tomcat 11.0.24). If nothing is blocked when you try
this, a newer Spring Boot release may already include the fix: check the gate output for jackson too.
</details>

### Mission 3.6 - Extend the golden path (show the facilitator)
Add a new question to the template, for example `"include_database": ["no", "yes"]` in
`cookiecutter.json`, and use it in `pom.xml` with
`{% if cookiecutter.include_database == "yes" %} ... {% endif %}`.

**Checkpoint:** generate twice (yes and no), run `mvn verify` in both, and show the facilitator two green builds.

## Discussion (5 min, with your neighbour)

1. You have 50 services generated from this template. The platform team improves the template.
   How do the 50 existing services get the improvement? (Hint: they don't, automatically.
   Look up `cruft` and "template drift".)
2. A team wants to use Go instead of Java. Should the platform say no, or offer a second golden path?
3. What should **never** be in a template?
