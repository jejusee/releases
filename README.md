# Release Hub

`jejusee/releases` is a project- and OS-independent distribution hub.

It owns the public distribution contract:

- version strategy and version validation
- prerelease/stable promotion
- GitHub Release creation
- immutable Release Assets
- SHA-256 metadata
- per-project `manifest.json`
- project-specific bootstrap installers and user documentation

Build and test logic stays in each development repository.

## Release model

A development repository asks the hub for a version, builds a finished package with that
version, uploads it as a workflow artifact, and asks the hub to publish it.

```text
plan -> project build/package -> publish
```

### Default strategy: SemVer

When `versioning.strategy` is omitted, the hub uses `semver` by default. The default
prerelease identifier is `dev`.

```json
"versioning": {
  "strategy": "semver",
  "prerelease": "dev"
}
```

The normal development operation is `dev` with one of these bump values:

| Bump | Meaning |
|---|---|
| `auto` | Continue the active prerelease; if none exists, start the next patch after Stable |
| `patch` | Use the next patch version based on Stable |
| `minor` | Use the next minor version based on Stable |
| `major` | Use the next major version based on Stable |
| `custom` | Use an explicitly supplied `MAJOR.MINOR.PATCH` target |

Examples:

```text
Stable 1.2.3 + auto       -> 1.2.4-dev.1
1.3.0-dev.4 + auto        -> 1.3.0-dev.5
Stable 1.2.3 + minor      -> 1.3.0-dev.1
Stable 1.2.3 + major      -> 2.0.0-dev.1
custom target 1.5.0       -> 1.5.0-dev.1
1.5.0-dev.7 + stable      -> 1.5.0
```

`release-stable` has no bump decision. It promotes the base version of the active
prerelease and clears the active prerelease channel.

The prerelease label is configurable per project. For example, `"prerelease": "rc"`
produces `1.3.0-rc.1` instead of `1.3.0-dev.1`.

Legacy operations `dev-major`, `dev-minor`, `dev-patch`, and `dev-rc` remain available
for existing callers, but new projects should use `dev` plus `bump`.

### Custom strategy

A project that does not use SemVer can declare:

```json
"versioning": {
  "strategy": "custom",
  "prerelease": "dev"
}
```

For this strategy the project supplies the exact version through `target_version`.
The hub does not calculate that project's version scheme, but still protects published
history and performs the common release/asset/manifest work.

## Safety rules

- A released version is never republished.
- Existing Release Assets are never overwritten.
- SemVer target versions cannot move backward from the active prerelease line.
- A Stable version already present in history cannot be reused as a new target.
- `publish.yml` verifies that the version returned by `plan.yml` is still the current
  expected version before creating the GitHub Release. A stale plan fails instead of
  silently publishing a different version.
- `manifest.json` is committed only after all assets are uploaded successfully.
- `versions` keeps immutable historical release metadata.

## Repository layout

```text
releases/
├── .github/
│   └── workflows/
│       ├── plan.yml
│       └── publish.yml
├── scripts/
│   └── release_hub.py
├── tests/
│   └── test_release_hub.py
├── examples/
│   └── caller/
│       └── release.yml
├── <project>/
│   ├── README.md
│   ├── install.sh / install.ps1
│   └── manifest.json
└── README.md
```

Project-specific Dev/Stable workflow files belong in the project's development
repository, not in this Release Hub repository.

## Project manifest

Each project owns `<project>/manifest.json`. `stable` and `prerelease` point to the
current channels; `versions` contains release history.

The hub supports arbitrary platform keys such as `linux-x64`, `linux-arm64`,
`windows-x64`, `windows-arm64`, `macos-arm64`, and `any`.

## Calling the hub

See `examples/caller/release.yml`. A project caller normally:

1. selects `auto`, `patch`, `minor`, `major`, or `custom` for a Dev release;
2. calls `plan.yml`;
3. builds/packages using the returned version;
4. uploads the finished package as a workflow artifact;
5. calls `publish.yml` with exactly the planned version.

A Stable workflow simply uses `operation: release-stable`.

## Required secret

Development repositories must provide `RELEASE_TOKEN` with the minimum permissions
needed to create Releases, upload Release Assets, and commit the changed project
manifest in `jejusee/releases`.

## Workflow version pinning

During hub development callers may use `@main`. After the contract is validated,
pin callers to a stable hub tag such as `@hub-v2` so later hub changes cannot
unexpectedly change existing projects.
