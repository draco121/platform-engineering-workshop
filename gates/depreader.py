"""
depreader.py - turn a Java project into a plain list of dependencies.

Every dependency gate starts the same way: "what libraries does this project
actually use?" This module answers that question in two ways:

  1. read_pom(path)        -> reads the <dependencies> you wrote in pom.xml
                              (direct dependencies only, no Maven needed)
  2. read_mvn_list(path)   -> reads the output of
                              `mvn dependency:list -DoutputFile=deps.txt`
                              (direct + transitive dependencies - the full truth)

Standard library only, so it runs anywhere Python 3.9+ runs.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    group: str
    artifact: str
    version: str
    scope: str = "compile"

    @property
    def name(self) -> str:
        """Maven coordinates as OSV and deps.dev expect them: group:artifact."""
        return f"{self.group}:{self.artifact}"

    def __str__(self) -> str:
        return f"{self.name}@{self.version}"


_PROP = re.compile(r"\$\{([^}]+)\}")


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _child_text(elem: ET.Element, name: str) -> str | None:
    for child in elem:
        if _strip_ns(child.tag) == name:
            return (child.text or "").strip()
    return None


def read_pom(path: str, include_test: bool = False) -> list[Dependency]:
    """Read direct dependencies from a pom.xml, resolving ${properties}."""
    root = ET.parse(path).getroot()

    props: dict[str, str] = {}
    for child in root:
        if _strip_ns(child.tag) == "properties":
            for p in child:
                props[_strip_ns(p.tag)] = (p.text or "").strip()
    props.setdefault("project.version", _child_text(root, "version") or "")

    deps: list[Dependency] = []
    for child in root:
        if _strip_ns(child.tag) != "dependencies":
            continue
        for d in child:
            group = _child_text(d, "groupId")
            artifact = _child_text(d, "artifactId")
            version = _child_text(d, "version")
            scope = _child_text(d, "scope") or "compile"
            if not (group and artifact):
                continue
            if version is None:
                # Version managed by a parent/BOM: only the full resolver knows it.
                print(f"  (skipping {group}:{artifact} - version is managed elsewhere; "
                      f"use --deps-file for the full picture)")
                continue
            version = _PROP.sub(lambda m: props.get(m.group(1), m.group(0)), version)
            if scope == "test" and not include_test:
                continue
            deps.append(Dependency(group, artifact, version, scope))
    return deps


# Lines look like:  "   org.yaml:snakeyaml:jar:1.33:compile -- module org.yaml.snakeyaml"
#              or:  "   com.foo:bar:jar:linux-x86_64:1.2.3:runtime"  (with a classifier)
_MVN_LINE = re.compile(r"^\s*([\w.\-]+):([\w.\-]+):[\w\-]+:(?:[\w.\-]+:)?([\w.\-+]+):(\w+)")


def read_mvn_list(path: str, include_test: bool = False) -> list[Dependency]:
    """Read the file produced by `mvn dependency:list -DoutputFile=<path>`."""
    deps: list[Dependency] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = _MVN_LINE.match(line)
            if not m:
                continue
            group, artifact, version, scope = m.groups()
            if scope == "test" and not include_test:
                continue
            deps.append(Dependency(group, artifact, version, scope))
    return sorted(set(deps), key=lambda d: d.name)


def load(pom: str | None, deps_file: str | None, include_test: bool = False) -> list[Dependency]:
    if deps_file:
        return read_mvn_list(deps_file, include_test)
    return read_pom(pom or "pom.xml", include_test)
