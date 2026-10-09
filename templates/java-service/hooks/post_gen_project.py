"""Runs AFTER generation: put code in the right Java package, drop optional parts, print next steps."""

import os
import shutil

PKG_PATH = "{{ cookiecutter.package_name }}".replace(".", os.sep)


def remove(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


# 1. Folder names can't contain "/", so the template uses a "_package_" placeholder.
#    Move it to e.g. src/main/java/dev/workshop/orders
for root in (os.path.join("src", "main", "java"), os.path.join("src", "test", "java")):
    placeholder = os.path.join(root, "_package_")
    target = os.path.join(root, PKG_PATH)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.move(placeholder, target)

# 2. Remove the optional parts the developer said "no" to.
if "{{ cookiecutter.include_example_api }}" != "yes":
    remove(os.path.join("src", "main", "java", PKG_PATH, "api"))
    remove(os.path.join("src", "test", "java", PKG_PATH, "api"))

if "{{ cookiecutter.include_dockerfile }}" != "yes":
    remove("Dockerfile")
    remove(".dockerignore")

print(r"""
  +--------------------------------------------------------------+
  |  {{ cookiecutter.service_name }} is ready.
  |
  |  Logging, tracing, metrics, health checks, error handling,
  |  formatting and CI gates are already wired in.
  |
  |  Next:
  |    cd {{ cookiecutter.service_slug }}
  |    mvn spring-boot:run
  |    curl localhost:{{ cookiecutter.server_port }}/actuator/health
  +--------------------------------------------------------------+
""")
