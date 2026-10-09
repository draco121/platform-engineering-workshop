# Platform-standard image: two stages (build, then a small runtime), runs as non-root.
FROM maven:3.9-eclipse-temurin-{{ cookiecutter.java_version }} AS build
WORKDIR /src
COPY pom.xml .
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B -q package -DskipTests -Dspotless.check.skip=true

FROM eclipse-temurin:{{ cookiecutter.java_version }}-jre
RUN useradd --system --uid 10001 app
USER app
WORKDIR /app
COPY --from=build /src/target/*.jar app.jar
EXPOSE {{ cookiecutter.server_port }}
# Kubernetes uses /actuator/health/liveness and /readiness as probes.
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
