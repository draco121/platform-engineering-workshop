"""Runs BEFORE any file is generated. Guardrail: reject bad names early, with a friendly message."""

import re
import sys

slug = "{{ cookiecutter.service_slug }}"
package = "{{ cookiecutter.package_name }}"
port = "{{ cookiecutter.server_port }}"

errors = []
if not re.fullmatch(r"[a-z][a-z0-9-]{2,40}", slug):
    errors.append(f"service_slug '{slug}' must be 3-41 chars of lowercase letters, digits and '-'.")
if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", package):
    errors.append(f"package_name '{package}' is not a valid Java package (e.g. dev.workshop.orders).")
if not port.isdigit() or not 1024 <= int(port) <= 65535:
    errors.append(f"server_port '{port}' must be a number between 1024 and 65535.")

if errors:
    print("\n[golden-path] Cannot generate the service:")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
