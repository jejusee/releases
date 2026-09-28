# Releases

여러 프로젝트의 **Public 배포 전용 저장소**입니다.

개발 소스는 각 Private 개발 저장소에서 관리하며, 이 저장소에서는 프로그램의 설치·업데이트와 배포 파일을 제공합니다.

---

# rclone-manager

Linux 서버에서 여러 rclone mount를 systemd 기반으로 간편하게 관리하는 도구입니다.

주요 기능:

- 여러 rclone mount를 인스턴스별로 관리
- systemd 자동 시작
- Read-only / Read-write
- VFS Cache
- 상태 및 통계 확인
- 간편 업데이트
- 기존 설정을 보존하는 안전한 삭제

## 설치

Linux 서버에서 다음 명령을 실행합니다.

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/installers/rclone-manager.sh | sudo bash
```

`curl`이 없다면:

```bash
wget -qO- https://raw.githubusercontent.com/jejusee/releases/main/installers/rclone-manager.sh | sudo bash
```

설치 확인:

```bash
rclonectl version
rclonectl help
```

> rclone-manager를 사용하려면 `rclone`이 먼저 설치되어 있어야 합니다.

---

## 업데이트

현재 설치된 버전 확인:

```bash
rclonectl version
```

Stable 최신 버전으로 업데이트:

```bash
sudo rclonectl update
```

특정 버전으로 업데이트:

```bash
sudo rclonectl update 0.2.0
```

RC 등 특정 버전도 직접 지정할 수 있습니다.

```bash
sudo rclonectl update 0.2.0-rc.1
```

업데이트 시 기존:

```text
/etc/rclone/rclone.conf
/etc/rclone/*.env
```

설정은 유지됩니다.

실행 중인 mount도 업데이트만으로 자동 재시작하지 않습니다.

필요한 경우 직접 재시작합니다.

```bash
sudo rclonectl restart all
```

---

## 삭제

### 프로그램만 삭제

기존 rclone 설정을 보존하면서 rclone-manager만 삭제합니다.

```bash
sudo rclonectl uninstall
```

일반적으로 이 방법을 사용하면 됩니다.

기존:

```text
/etc/rclone/rclone.conf
/etc/rclone/*.env
```

설정은 그대로 남으므로 나중에 다시 설치해 재사용할 수 있습니다.

### 설정까지 삭제

rclone-manager 설정까지 함께 제거하려면:

```bash
sudo rclonectl uninstall --purge
```

`--purge` 사용 시 `rclone.conf`, `*.env`, `remote.env.example`도 제거되므로 필요한 설정은 먼저 백업하세요.

mount 디렉터리와 VFS cache 디렉터리는 자동으로 삭제하지 않습니다.

---

## 상세 사용법

처음 설정하거나 새로운 mount를 추가하려면 다음 사용자 가이드를 참고하세요.

**[rclone-manager 사용 가이드](docs/rclone-manager.md)**

사용 가이드에는 다음 내용이 포함되어 있습니다.

- rclone Remote 설정
- `/etc/rclone/*.env` 설정
- Mount 인스턴스 추가
- 시작 / 중지 / 재시작
- 부팅 시 자동 시작
- Read-only / Read-write
- VFS Cache 설정
- 상태 및 통계 확인
- 전체 `rclonectl` 명령
- 문제 해결

---

## 빠른 명령

```bash
# 인스턴스 목록
rclonectl list

# 상태 확인
rclonectl status all

# 설정 검사
sudo rclonectl check all

# 시작
sudo rclonectl start media

# 중지
sudo rclonectl stop media

# 재시작
sudo rclonectl restart media

# 자동 시작
sudo rclonectl enable media

# 로그
rclonectl log media

# 현재 버전
rclonectl version

# 업데이트
sudo rclonectl update

# 삭제 (설정 유지)
sudo rclonectl uninstall
```

---

## 배포 구조

```text
releases/
├── README.md
├── docs/
│   └── rclone-manager.md
├── installers/
│   └── rclone-manager.sh
└── manifests/
    └── rclone-manager.json
```

실제 `.tar.gz`, `.zip`, `.exe` 등의 프로그램 패키지는 Git 저장소에 Commit하지 않고 **GitHub Release Assets**로 배포합니다.

현재 Stable/Prerelease 버전과 다운로드 위치는:

```text
manifests/rclone-manager.json
```

에서 관리합니다.

Release 버전이 변경될 때마다 README를 수정할 필요는 없습니다. **설치 방법이나 사용 방법 자체가 변경된 경우에만 README 또는 사용자 가이드를 갱신합니다.**
