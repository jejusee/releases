#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-rc\.(0|[1-9]\d*))?$")
PROJECT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
PLATFORM = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def die(message: str) -> None:
    raise SystemExit(message)


def parse_version(value: str) -> tuple[int, int, int, int | None]:
    m = SEMVER.fullmatch(value)
    if not m:
        die(f"Invalid version: {value}")
    major, minor, patch = map(int, m.group(1, 2, 3))
    rc = int(m.group(4)) if m.group(4) is not None else None
    return major, minor, patch, rc


def empty_manifest(project: str) -> dict[str, Any]:
    return {
        "schema": 2,
        "project": project,
        "stable": None,
        "prerelease": None,
        "versions": {},
    }


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

    for channel in ("stable", "prerelease"):
        item = data.get(channel)
        if item is not None:
            validate_release_entry(item)

    for version, item in data["versions"].items():
        parse_version(version)
        validate_release_entry(item)
        if item["version"] != version:
            die(f"versions[{version!r}] has mismatched version")

    return data


def validate_release_entry(item: Any) -> None:
    if not isinstance(item, dict):
        die("Release entry must be an object")
    version = item.get("version")
    if not isinstance(version, str):
        die("Release entry version is missing")
    parse_version(version)
    if not isinstance(item.get("published_at"), str):
        die(f"Release {version} has no published_at")
    assets = item.get("assets")
    if not isinstance(assets, dict) or not assets:
        die(f"Release {version} must contain assets")
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


def next_version(manifest: dict[str, Any], operation: str) -> str:
    stable = manifest.get("stable")
    pre = manifest.get("prerelease")

    if operation in {"dev-patch", "dev-minor", "dev-major"}:
        if pre is not None:
            die(
                f"Cannot start {operation}: active prerelease "
                f"{pre['version']} exists. Use dev-rc or release-stable first."
            )
        if stable is None:
            base = (0, 0, 0)
        else:
            major, minor, patch, rc = parse_version(stable["version"])
            if rc is not None:
                die("stable cannot contain an rc version")
            base = (major, minor, patch)

        major, minor, patch = base
        if operation == "dev-patch":
            patch += 1
        elif operation == "dev-minor":
            minor += 1
            patch = 0
        else:
            major += 1
            minor = 0
            patch = 0
        return f"{major}.{minor}.{patch}-rc.1"

    if operation == "dev-rc":
        if pre is None:
            die("Cannot update RC: no active prerelease. Start with dev-major, dev-minor, or dev-patch.")
        major, minor, patch, rc = parse_version(pre["version"])
        if rc is None:
            die("prerelease must be an rc version")
        return f"{major}.{minor}.{patch}-rc.{rc + 1}"

    if operation == "release-stable":
        if pre is None:
            die("Cannot release stable: no active prerelease.")
        major, minor, patch, rc = parse_version(pre["version"])
        if rc is None:
            die("prerelease must be an rc version")
        return f"{major}.{minor}.{patch}"

    die(f"Unknown operation: {operation}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cmd_next(args: argparse.Namespace) -> None:
    manifest = load_manifest(Path(args.manifest), args.project)
    version = next_version(manifest, args.operation)
    print(version)


def cmd_update(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path, args.project)

    expected = next_version(manifest, args.operation)
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
        platform = item.get("platform")
        filename = item.get("file")
        if not isinstance(platform, str) or not PLATFORM.fullmatch(platform):
            die(f"Invalid platform in asset spec: {platform!r}")
        if platform in assets:
            die(f"Duplicate platform in asset spec: {platform}")
        if not isinstance(filename, str) or Path(filename).name != filename:
            die(f"Asset file must be a plain filename: {filename!r}")

        path = assets_dir / filename
        if not path.is_file():
            die(f"Asset not found: {path}")

        url = (
            f"https://github.com/{args.repository}/releases/download/"
            f"{args.tag}/{filename}"
        )
        assets[platform] = {
            "url": url,
            "sha256": sha256(path),
        }

    published_at = args.published_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entry = {
        "version": args.version,
        "published_at": published_at,
        "assets": assets,
    }

    manifest["versions"][args.version] = entry
    if args.operation == "release-stable":
        manifest["stable"] = entry
        manifest["prerelease"] = None
    else:
        manifest["prerelease"] = entry

    # Deterministic top-level shape.
    result = {
        "schema": 2,
        "project": args.project,
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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Release Hub helper")
    sub = p.add_subparsers(dest="command", required=True)

    n = sub.add_parser("next")
    n.add_argument("--project", required=True)
    n.add_argument("--manifest", required=True)
    n.add_argument("--operation", required=True, choices=["dev-major", "dev-minor", "dev-patch", "dev-rc", "release-stable"])
    n.set_defaults(func=cmd_next)

    u = sub.add_parser("update")
    u.add_argument("--project", required=True)
    u.add_argument("--manifest", required=True)
    u.add_argument("--operation", required=True, choices=["dev-major", "dev-minor", "dev-patch", "dev-rc", "release-stable"])
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
