# rclone-manager Distribution

이 폴더는 rclone-manager의 공개 배포 진입점입니다.

- `manifest.json`: stable/prerelease/version별 asset metadata
- `install.sh`: 공통 `bootstrap/install.sh`를 rclone-manager로 호출하는 얇은 wrapper

설치:

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash
```

특정 버전:

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- 0.2.0-rc.1
```
