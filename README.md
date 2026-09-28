# Release Hub

`jejusee/releases` is a project- and OS-independent distribution hub.

It owns the public distribution contract:

- semantic version calculation
- prerelease/stable promotion
- GitHub Release creation
- immutable Release Assets
- SHA-256 metadata
- per-project `manifest.json`
- project-specific bootstrap installers and user documentation

Build and test logic stays in each development repository.

## Release model

A development repository builds a finished package, uploads it as a workflow artifact,
then calls the reusable workflows in this repository.

The public caller still exposes only one **Release** Action. Internally the hub uses
two reusable stages so projects can embed the calculated version before packaging:

`plan -> project build/package -> publish`.

Release types:

| Type | Meaning |
|---|---|
| `patch` | Start a new patch RC from stable (`1.2.3` -> `1.2.4-rc.1`) |
| `minor` | Start a new minor RC from stable (`1.2.3` -> `1.3.0-rc.1`) |
| `major` | Start a new major RC from stable (`1.2.3` -> `2.0.0-rc.1`) |
| `beta` | Increment the current RC (`1.3.0-rc.1` -> `1.3.0-rc.2`) |
| `release` | Promote the current RC (`1.3.0-rc.2` -> `1.3.0`) |

Rules:

- `beta` requires an existing prerelease.
- `release` requires an existing prerelease.
- `patch`, `minor`, and `major` require no active prerelease.
- A released version is never republished.
- Existing Release Assets are never overwritten.
- `manifest.json` is updated only after all assets are uploaded successfully.
- `stable` is not changed by RC releases.
- `versions` keeps immutable historical metadata.

## Repository layout

```text
releases/
├── .github/
│   └── workflows/
│       ├── plan.yml
│       └── publish.yml
├── scripts/
│   └── release_hub.py
├── examples/
│   └── caller/
│       └── release.yml
├── <project>/
│   ├── README.md
│   ├── install.sh / install.ps1
│   └── manifest.json
└── README.md
```

## Project manifest

Each project owns `<project>/manifest.json`.

The hub supports any platform key, for example:

- `linux-x64`
- `linux-arm64`
- `windows-x64`
- `windows-arm64`
- `macos-arm64`
- `any`

A release may contain multiple assets/platforms.

## Calling the hub

Each development repository keeps only a small caller workflow. See
`examples/caller/release.yml`.

The caller:

1. chooses `beta`, `patch`, `minor`, `major`, or `release`;
2. asks the hub for the next version;
3. builds/packages using that version;
4. uploads the finished files as one workflow artifact;
5. calls the hub to publish them.

This repository does not need to know whether the package was produced by Bash,
.NET, Python, Node.js, or another tool.

## Required secret

Development repositories must provide `RELEASE_TOKEN`.

The token must be able to:

- create Releases in `jejusee/releases`;
- upload Release Assets;
- commit and push the changed project manifest.

Use the minimum repository scope required for `jejusee/releases`.

## Workflow version pinning

During initial development a caller can use:

```yaml
uses: jejusee/releases/.github/workflows/plan.yml@main
```

After the hub is validated, create a stable hub tag such as `hub-v1` and pin callers:

```yaml
uses: jejusee/releases/.github/workflows/plan.yml@hub-v1
```

That prevents future hub maintenance from unexpectedly changing existing projects.
