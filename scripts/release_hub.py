#!/usr/bin/env python3
"""Release hub version planning and manifest maintenance (Python 3.8+)."""
import argparse
import datetime
import json
import re
from pathlib import Path

SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?$')
PROJECT = re.compile(r'^[a-z0-9][a-z0-9._-]*$')

def fail(message):
    raise SystemExit(message)

def parse(version):
    match = SEMVER.fullmatch(version)
    if not match:
        fail('Invalid semantic version: ' + version)
    return tuple(int(match.group(i)) for i in (1, 2, 3)), match.group(4)

def empty(project):
    return {'schema': 2, 'project': project, 'stable': None, 'prerelease': None, 'versions': {}}

def load(path, project):
    if not PROJECT.fullmatch(project):
        fail('Invalid project: ' + project)
    data = json.loads(path.read_text('utf-8')) if path.exists() else empty(project)
    if data.get('project') != project or not isinstance(data.get('versions'), dict):
        fail('Invalid manifest project/versions')
    return data

def latest_stable(data):
    versions = [v for v in data['versions'] if parse(v)[1] is None]
    return max(versions, key=lambda v: parse(v)[0]) if versions else None

def next_version(data, operation, bump, target):
    if operation not in ('dev', 'release-stable', 'dev-major', 'dev-minor', 'dev-patch', 'dev-rc'):
        fail('Invalid operation')
    if bump not in ('auto', 'patch', 'minor', 'major', 'custom'):
        fail('Invalid bump')
    versions = data['versions']
    stable = latest_stable(data)
    stable_base = parse(stable)[0] if stable else (0, 0, 0)
    devs = [(parse(v)[0], int(parse(v)[1].split('.')[1]), v)
            for v in versions if parse(v)[1] and re.fullmatch(r'(?:dev|rc)\.\d+', parse(v)[1])]
    # Preserve the prerelease label already used by the project (e.g. rc).
    cfg = data.get('versioning') or {}
    label = cfg.get('prerelease') or ('rc' if any('-rc.' in v for v in versions) else 'dev')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*', label):
        fail('Invalid prerelease label')
    if operation == 'release-stable':
        if not devs:
            fail('No prerelease to promote')
        base = max(devs, key=lambda x: (x[0], x[1]))[0]
        version = '.'.join(map(str, base))
        if version in versions:
            fail('Stable version already published: ' + version)
        return version
    if operation.startswith('dev-'):
        bump = {'dev-major':'major','dev-minor':'minor','dev-patch':'patch','dev-rc':'auto'}[operation]
    if bump == 'custom':
        if not target:
            fail('Custom requires --target-version')
        base, suffix = parse(target)
        if suffix is not None:
            fail('Custom target must be MAJOR.MINOR.PATCH')
    elif bump == 'auto' and devs:
        base = max(devs, key=lambda x: (x[0], x[1]))[0]
    else:
        major, minor, patch = stable_base
        if bump == 'major': base = (major + 1, 0, 0)
        elif bump == 'minor': base = (major, minor + 1, 0)
        else: base = (major, minor, patch + 1)
    prefix = '.'.join(map(str, base)) + '-' + label + '.'
    indexes = [int(v[len(prefix):]) for v in versions if v.startswith(prefix) and v[len(prefix):].isdigit()]
    return prefix + str(max(indexes, default=0) + 1)

def publish(data, version, assets, repository):
    parse(version)
    if version in data['versions']:
        fail('Version already published: ' + version)
    if not isinstance(assets, dict) or not assets:
        fail('Assets must be a nonempty mapping')
    for platform, value in assets.items():
        if not PROJECT.fullmatch(platform) or not isinstance(value, dict):
            fail('Invalid asset')
        if not value.get('url', '').startswith('https://github.com/' + repository + '/releases/download/'):
            fail('Invalid asset URL')
        if not re.fullmatch('[0-9a-f]{64}', value.get('sha256', '')):
            fail('Invalid sha256')
    record = {'version': version, 'published_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'assets': assets}
    data['versions'][version] = record
    if parse(version)[1] is None:
        data['stable'] = record
    else:
        data['prerelease'] = record
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['next', 'publish'])
    parser.add_argument('--project', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--operation', default='dev')
    parser.add_argument('--bump', default='auto')
    parser.add_argument('--target-version', default='')
    parser.add_argument('--version', default='')
    parser.add_argument('--assets-json', default='')
    parser.add_argument('--repository', default='jejusee/releases')
    args = parser.parse_args()
    path = Path(args.manifest)
    data = load(path, args.project)
    if args.command == 'next':
        print(next_version(data, args.operation, args.bump, args.target_version))
    else:
        if not args.version:
            fail('--version is required')
        updated = publish(data, args.version, json.loads(Path(args.assets_json).read_text('utf-8')), args.repository)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
