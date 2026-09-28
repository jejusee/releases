# rclone-manager

Public distribution metadata and documentation for `rclone-manager`.

Files in this folder form the stable public interface for installation and updates:

- `manifest.json` — release/update metadata
- `install.sh` — bootstrap installer (add the project's production installer here)
- `README.md` — user documentation

The shared Release Hub workflow updates only `manifest.json`.
Project documentation and bootstrap installers are not rewritten during releases.


# 설치방법
```
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash
```
