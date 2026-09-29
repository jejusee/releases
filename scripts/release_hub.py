#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
BASE_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PROJECT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
IDENTIFIER = re.compile(r"^[0-9A-Za-z-]+$")
PLATFORM = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
CUSTOM_VERSION = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+-]*$")

NEW_OPERATIONS = {"dev", "release-stable"}
LEGACY_OPERATIONS = {"dev-major", "dev-minor", "dev-patch", "dev-rc"}
OPERATIONS = NEW_OPERATIONS | LEGACY_OPERATIONS
BUMPS = {"auto", "patch", "minor", "major", "custom"}


def die(message: str) -> None:
    raise SystemExit(message)


def parse_semver(value: str) -> tuple[int, int, int, str | None, str | None]:
    m = SEMVER.fullmatch(value)
    if not m:
        die(f"Invalid semantic version: {value}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), m.group(5)


def parse_base(value: str) -> tuple[int, int, int]:
    m = BASE_SEMVER.fullmatch(value)
    if not m:
        die(f"Target version must be MAJOR.MINOR.PATCH only: {value}")
    return tuple(map(int, m.group(1, 2, 3)))


def base_of(value: str) -> tuple[int, int, int]:
    major, minor, patch, _, _ = parse_semver(value)
    return major, minor, patch


def versioning(manifest: dict[str, Any]) -> dict[str, str]:
    cfg = manifest.get("versioning")
    if cfg is None:
        # Schema-2 manifests created before version strategies existed remain valid.
        return {"strategy": "semver", "prerelease": "dev"}
    if not isinstance(cfg, dict):
        die("versioning must be an object")

    strategy = cfg.get("strategy", "semver")
    prerelease = cfg.get("prerelease", "dev")
    if strategy not in {"semver", "custom"}:
        die(f"Unsupported versioning strategy: {strategy}")
    if not isinstance(prerelease, str) or not IDENTIFIER.fullmatch(prerelease):
        die(f"Invalid prerelease identifier: {prerelease!r}")
    return {"strategy": strategy, "prerelease": prerelease}


def empty_manifest(project: str) -> dict[str, Any]:
    return {
        "schema": 2,
        "project": project,
        "versioning": {"strategy": "semver", "prerelease": "dev"},
        "stable": None,
        "prerelease": None,
        "versions": {},
    }


def validate_version(value: str, strategy: str) -> None:
    if strategy == "semver":
        parse_semver(value)
    elif not CUSTOM_VERSION.fullmatch(value):
        die(f"Invalid custom version: {value}")


def load_manifest(path: Path, project: str) -> dict[str, Any]:
    if not PROJECT.fullmatch(project):
        die(f"Invalid project name: {project}")
    if not path.exists():
        return empty_manifest(project)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"Cannot read manifest {path}: {exc}")
