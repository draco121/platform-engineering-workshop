# {{ cookiecutter.service_name }}

{{ cookiecutter.description }}

Owned by **{{ cookiecutter.owner_team }}**. Generated from the platform golden path.

## Run it

```bash
mvn spring-boot:run
curl localhost:{{ cookiecutter.server_port }}/actuator/health
{%- if cookiecutter.include_example_api == "yes" %}
curl "localhost:{{ cookiecutter.server_port }}/api/greeting?name=you"
{%- endif %}
```

## What you got for free

| Concern | Where | What it does |
|---|---|---|
| Structured logs | `application.yml` → `logging.structured` | Every log line is JSON, searchable by `requestId` and `traceId` |
| Request ids | `platform/RequestIdFilter.java` | Every response carries `X-Request-Id` |
| Tracing | `spring-boot-starter-opentelemetry` | Sends traces to `OTEL_EXPORTER_OTLP_ENDPOINT` |
| Metrics | `/actuator/prometheus` | Request counts, latencies, JVM stats |
| Health checks | `/actuator/health/liveness`, `/readiness` | Ready for Kubernetes probes |
| Error format | `spring.mvc.problemdetails` | Errors are JSON (RFC 9457), never stack traces |
| Formatting | Spotless + google-java-format | `mvn verify` fails on bad formatting, `mvn spotless:apply` fixes it |
| CI + gates | `.github/workflows/ci.yml` | Build, test, then the central security and license gates |
| Catalog entry | `catalog-info.yaml` | Shows up in the developer portal with its owner |
{%- if cookiecutter.include_dockerfile == "yes" %}
| Container | `Dockerfile` | Small, non-root image with a health check |
{%- endif %}

## Write your feature

Add your code under `src/main/java/{{ cookiecutter.package_name.replace('.', '/') }}/`. Everything above keeps working.
