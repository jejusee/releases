# rclone-manager

Linux 서버의 rclone mount 인스턴스를 systemd와 `rclonectl`로 관리합니다.

## 배포 서버에서 설치

### 최신 안정버전(Stable)
```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash
```

버전을 생략하면 최신 Stable을 설치합니다. Stable이 없으면 개발버전을 자동 설치하지 않고 오류로 종료합니다.

### 최신 개발버전(RC)
```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- --dev
```

### 특정 버전
```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- 0.1.0-rc.3
```

## 설치 후 기본 사용
```bash
rclonectl version
sudo rclonectl create media
sudo vi /etc/rclone/media.env
sudo vi /etc/rclone/media.filter
sudo rclonectl check media
sudo rclonectl enable media
sudo rclonectl start media
rclonectl status media
```

## 업데이트
설치와 업데이트는 같은 버전 선택 규칙을 사용합니다.

```bash
sudo rclonectl update                 # 최신 Stable
sudo rclonectl update --dev           # 최신 개발버전(RC)
sudo rclonectl update 0.1.0-rc.3      # 정확한 지정 버전
sudo rclonectl update 1.0.0           # 정확한 지정 버전
```

Stable이 없으면 `update`가 RC를 자동 설치하지 않고 `--dev` 사용을 안내합니다.

업데이트는 실행 중인 mount를 자동 재시작하지 않습니다.
```bash
sudo rclonectl restart all
```

## 삭제
```bash
sudo rclonectl uninstall
sudo rclonectl uninstall --purge
```

기본 uninstall은 `/etc/rclone` 사용자 설정을 보존합니다.

---

이 폴더는 공개 배포 인터페이스입니다.

- `manifest.json` — Stable / 개발(RC) / 과거 버전 메타데이터
- `install.sh` — 설치 bootstrap wrapper
- `README.md` — 배포 서버 사용 설명

Release Hub workflow는 릴리스 시 `manifest.json`만 자동 갱신합니다.
