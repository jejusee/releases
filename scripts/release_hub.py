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

    if data.get("schema") != 2:
        die("Unsupported manifest schema; expected schema 2")
    if data.get("project") != project:
        die(f"Manifest project mismatch: expected {project!r}")
    if not isinstance(data.get("versions"), dict):
        die("Manifest versions must be an object")

    cfg = versioning(data)
    for channel in ("stable", "prerelease"):
        item = data.get(channel)
        if item is not None:
            validate_release_entry(item, cfg["strategy"])
    for ver, item in data["versions"].items():
        validate_version(ver, cfg["strategy"])
        validate_release_entry(item, cfg["strategy"])
        if item["version"] != ver:
            die(f"versions[{ver!r}] has mismatched version")
    return data


def validate_release_entry(item: Any, strategy: str = "semver") -> None:
    if not isinstance(item, dict):
        die("Release entry must be an object")
    ver = item.get("version")
    if not isinstance(ver, str):
        die("Release entry version is missing")
    validate_version(ver, strategy)
    if not isinstance(item.get("published_at"), str):
        die(f"Release {ver} has no published_at")
    assets = item.get("assets")
    if not isinstance(assets, dict) or not assets:
        die(f"Release {ver} must contain assets")
    for platform, asset in assets.items():
        if not PLATFORM.fullmatch(platform):
            die(f"Invalid platform key: {platform}")
        if not isinstance(asset, dict):
            die(f"Invalid asset metadata for {platform}")
        if not isinstance(asset.get("url"), str) or not asset["url"].startswith("https://"):
            die(f"Invalid asset URL for {platform}")
        sha = asset.get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            die(f"Invalid SHA256 for {platform}")


def next_prerelease_number(manifest: dict[str, Any], base: tuple[int, int, int], label: str) -> int:
    prefix = f"{base[0]}.{base[1]}.{base[2]}-{label}."
    highest = 0
    for ver in manifest["versions"]:
        if not ver.startswith(prefix):
            continue
        suffix = ver[len(prefix):]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return highest + 1


def ensure_new_base(manifest: dict[str, Any], base: tuple[int, int, int]) -> None:
    stable = manifest.get("stable")
    if stable is not None and base <= base_of(stable["version"]):
        die(f"Target version {'.'.join(map(str, base))} must be greater than stable {stable['version']}")

    # A previously abandoned prerelease line cannot be reopened after moving on.
    pre = manifest.get("prerelease")
    if pre is not None and base < base_of(pre["version"]):
        die(f"Target version cannot move backward from active prerelease {pre['version']}")

    stable_version = f"{base[0]}.{base[1]}.{base[2]}"
    if stable_version in manifest["versions"]:
        die(f"Target version was already published as stable: {stable_version}")


def next_semver(manifest: dict[str, Any], operation: str, bump: str, target: str | None) -> str:
    cfg = versioning(manifest)
    label = cfg["prerelease"]
    stable = manifest.get("stable")
    pre = manifest.get("prerelease")

    if operation == "release-stable":
        if pre is None:
            die("Cannot release stable: no active prerelease")
        major, minor, patch, prerelease, build = parse_semver(pre["version"])
        if prerelease is None or build is not None:
            die("Active prerelease is not a promotable semantic prerelease")
        return f"{major}.{minor}.{patch}"

    if operation != "dev":
        die(f"Unsupported semver operation: {operation}")
    if bump not in BUMPS:
        die(f"Invalid bump: {bump}")

    if bump == "auto" and target:
        die("target-version is only valid with bump=custom")

    if bump == "auto":
        if pre is not None:
            base = base_of(pre["version"])
        else:
            if stable is None:
                die("First prerelease requires patch/minor/major or custom target version")
            major, minor, patch = base_of(stable["version"])
            base = (major, minor, patch + 1)
    elif bump == "custom":
        if not target:
            die("bump=custom requires --target-version MAJOR.MINOR.PATCH")
        base = parse_base(target)
    else:
        if target:
            die("target-version is only valid with bump=custom")
        base = base_of(stable["version"]) if stable is not None else (0, 0, 0)
        major, minor, patch = base
        if bump == "patch":
            base = (major, minor, patch + 1)
        elif bump == "minor":
            base = (major, minor + 1, 0)
        else:
            base = (major + 1, 0, 0)

    ensure_new_base(manifest, base)
    number = next_prerelease_number(manifest, base, label)
    return f"{base[0]}.{base[1]}.{base[2]}-{label}.{number}"


def next_legacy(manifest: dict[str, Any], operation: str) -> str:
    stable = manifest.get("stable")
    pre = manifest.get("prerelease")
    if operation in {"dev-patch", "dev-minor", "dev-major"}:
        if pre is not None:
            die(f"Cannot start {operation}: active prerelease {pre['version']} exists")
        base = base_of(stable["version"]) if stable is not None else (0, 0, 0)
        major, minor, patch = base
        if operation == "dev-patch": patch += 1
        elif operation == "dev-minor": minor, patch = minor + 1, 0
        else: major, minor, patch = major + 1, 0, 0
        return f"{major}.{minor}.{patch}-rc.1"
    if operation == "dev-rc":
        if pre is None:
            die("Cannot update RC: no active prerelease")
        major, minor, patch, prerelease, build = parse_semver(pre["version"])
        m = re.fullmatch(r"rc\.(\d+)", prerelease or "")
        if not m or build is not None:
            die("Legacy dev-rc requires an rc.N prerelease")
        return f"{major}.{minor}.{patch}-rc.{int(m.group(1)) + 1}"
    die(f"Unknown legacy operation: {operation}")


def next_version(manifest: dict[str, Any], operation: str, bump: str = "auto", target: str | None = None) -> str:
    if operation not in OPERATIONS:
        die(f"Unknown operation: {operation}")
    if operation in LEGACY_OPERATIONS:
        return next_legacy(manifest, operation)

    cfg = versioning(manifest)
    if cfg["strategy"] == "semver":
        return next_semver(manifest, operation, bump, target)

    # Custom strategy: project supplies the exact version. Hub only protects history/channels.
    if not target:
        die("custom versioning strategy requires --target-version")
    validate_version(target, "custom")
    if target in manifest["versions"]:
        die(f"Version already exists in manifest: {target}")
    return target


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cmd_next(args: argparse.Namespace) -> None:
    manifest = load_manifest(Path(args.manifest), args.project)
    print(next_version(manifest, args.operation, args.bump, args.target_version))


def cmd_update(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path, args.project)
    expected = next_version(manifest, args.operation, args.bump, args.target_version)
    if args.version != expected:
        die(f"Version race/mismatch: expected {expected}, got {args.version}")
    if args.version in manifest["versions"]:
        die(f"Version already exists in manifest: {args.version}")

    assets_dir = Path(args.assets_dir)
    spec = json.loads(Path(args.asset_spec).read_text(encoding="utf-8"))
    if not isinstance(spec, list) or not spec:
        die("asset spec must be a non-empty JSON array")

    assets: dict[str, Any] = {}
    for item in spec:
        platform, filename = item.get("platform"), item.get("file")
        if not isinstance(platform, str) or not PLATFORM.fullmatch(platform):
            die(f"Invalid platform in asset spec: {platform!r}")
        if platform in assets:
            die(f"Duplicate platform in asset spec: {platform}")
        if not isinstance(filename, str) or Path(filename).name != filename:
            die(f"Asset file must be a plain filename: {filename!r}")
        path = assets_dir / filename
        if not path.is_file():
            die(f"Asset not found: {path}")
        assets[platform] = {
            "url": f"https://github.com/{args.repository}/releases/download/{args.tag}/{filename}",
            "sha256": sha256(path),
        }

    published_at = args.published_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entry = {"version": args.version, "published_at": published_at, "assets": assets}
    manifest["versions"][args.version] = entry
    if args.operation == "release-stable":
        manifest["stable"] = entry
        manifest["prerelease"] = None
    else:
        manifest["prerelease"] = entry

    result = {
        "schema": 2,
        "project": args.project,
        "versioning": versioning(manifest),
        "stable": manifest.get("stable"),
        "prerelease": manifest.get("prerelease"),
        "versions": manifest["versions"],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(manifest_path)


def cmd_validate(args: argparse.Namespace) -> None:
    load_manifest(Path(args.manifest), args.project)
    print("ok")


def add_version_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--operation", required=True, choices=sorted(OPERATIONS))
    parser.add_argument("--bump", default="auto", choices=sorted(BUMPS))
    parser.add_argument("--target-version")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Release Hub helper")
    sub = p.add_subparsers(dest="command", required=True)
    n = sub.add_parser("next")
    n.add_argument("--project", required=True)
    n.add_argument("--manifest", required=True)
    add_version_args(n)
    n.set_defaults(func=cmd_next)

    u = sub.add_parser("update")
    u.add_argument("--project", required=True)
    u.add_argument("--manifest", required=True)
    add_version_args(u)
    u.add_argument("--version", required=True)
    u.add_argument("--repository", required=True)
    u.add_argument("--tag", required=True)
    u.add_argument("--assets-dir", required=True)
    u.add_argument("--asset-spec", required=True)
    u.add_argument("--published-at")
    u.set_defaults(func=cmd_update)

    v = sub.add_parser("validate")
    v.add_argument("--project", required=True)
    v.add_argument("--manifest", required=True)
    v.set_defaults(func=cmd_validate)
    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
