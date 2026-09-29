# rclone-manager

`rclone-manager`는 Linux 서버에서 여러 rclone mount 인스턴스를 systemd와 `rclonectl`로 관리하기 위한 도구입니다.

> 이 문서는 **배포/사용자용 README**입니다. 개발 방법, Git 작업, Release workflow 등 개발자 문서는 `rclone-manager-dev` 저장소에서 관리합니다.

---

## 1. 사전 준비

### 1-1. rclone 설치

`rclone-manager`는 rclone 자체를 포함하지 않습니다. 먼저 rclone을 설치하고 remote를 구성해야 합니다.

아래 두 방식 중 하나를 선택할 수 있습니다. `rclone-manager`는 실행 가능한 `rclone` 명령을 사용하므로 공식판과 Mod판을 별도로 구분하지 않습니다.

#### 방법 A. wiserain/rclone Mod 버전

추가 기능이 포함된 Mod 버전을 사용하는 경우:

```bash
curl -fsSL "https://raw.githubusercontent.com/wiserain/rclone/mod/install.sh" | sudo bash
```

설치 확인:

```bash
rclone version
```

Mod 버전 업데이트도 같은 명령을 다시 실행합니다.

```bash
curl -fsSL "https://raw.githubusercontent.com/wiserain/rclone/mod/install.sh" | sudo bash
```

> Mod 버전을 계속 사용할 경우 공식판으로 바뀌는 것을 피하기 위해 `rclone selfupdate` 대신 위 설치 스크립트로 업데이트합니다.

프로젝트: https://github.com/wiserain/rclone/tree/mod

#### 방법 B. rclone 공식 버전

```bash
sudo -v
curl https://rclone.org/install.sh | sudo bash
```

설치 확인:

```bash
rclone version
```

공식 버전 업데이트:

```bash
sudo rclone selfupdate
```

공식 설치 문서: https://rclone.org/install/

> `rclonectl update`는 **rclone-manager 자체**를 업데이트합니다. rclone 프로그램 업데이트와는 별개입니다.

### 1-2. rclone remote 설정

```bash
rclone config
rclone listremotes
```

예:

```text
gdm:
gds:
onedrive:
```

`rclone-manager`의 systemd 서비스는 `/etc/rclone/rclone.conf`를 사용합니다. 사용할 remote가 이 설정 파일에 준비되어 있어야 합니다.

---

## 2. rclone-manager 설치

### 최신 Stable

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash
```

### 최신 개발버전(RC)

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- --dev
```

### 특정 버전

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- 0.1.0-rc.3
```

설치 확인:

```bash
rclonectl version
```

Stable이 아직 배포되지 않은 경우 일반 설치가 RC로 자동 전환되지 않습니다. 이 경우 `--dev`를 명시합니다.

---

## 3. 인스턴스 만들기

예를 들어 `gdm` 인스턴스를 생성합니다.

```bash
sudo rclonectl create gdm
```

생성되는 주요 설정 파일:

```text
/etc/rclone/gdm.env
/etc/rclone/gdm.filter
```

### 최소 `.env` 설정

`.env`는 전체 설정 복사본이 아니라 **인스턴스별 override 파일**입니다. 기본적으로 다음 값만 지정하면 됩니다.

```ini
REMOTE_PATH=gdm:
MOUNT_PATH=/mnt/gdm
RC_PORT=5572
```

선택 항목은 생략하거나 주석 처리하면 rclone-manager의 현재 기본값을 사용합니다. 특정 인스턴스만 다르게 설정할 항목만 활성화합니다.

```ini
# 기본값 사용
# BUFFER_SIZE=32M

# 이 인스턴스만 변경
BUFFER_SIZE=64M
```

현재 기본값:

```text
CACHE_DIR=/var/cache/rclone/<instance>
READ_ONLY=true
VFS_CACHE_MODE=full
VFS_CACHE_MAX_SIZE=50G
VFS_CACHE_MAX_AGE=24h
VFS_CACHE_POLL_INTERVAL=1m
BUFFER_SIZE=32M
VFS_READ_AHEAD=128M
VFS_READ_CHUNK_SIZE=64M
VFS_READ_CHUNK_SIZE_LIMIT=1G
VFS_READ_CHUNK_STREAMS=0
DIR_CACHE_TIME=1000h
POLL_INTERVAL=1m
VFS_WRITE_BACK=30s
TRANSFERS=4
```

`rclonectl create`로 생성되는 `.env`에는 각 옵션 설명과 기본값이 주석으로 포함됩니다. 특별한 이유가 없다면 선택값을 불필요하게 고정하지 않는 것을 권장합니다.

---

## 4. 설정 확인 및 시작

```bash
sudo rclonectl check gdm
sudo rclonectl enable gdm
sudo rclonectl start gdm
rclonectl status gdm
```

설정을 변경한 뒤 적용하려면:

```bash
sudo rclonectl restart gdm
```

전체 인스턴스를 재시작하려면:

```bash
sudo rclonectl restart all
```

---

## 5. 주요 명령

```text
rclonectl create <instance>
rclonectl list
rclonectl status [instance|all]
rclonectl start [instance|all]
rclonectl stop [instance|all]
rclonectl restart [instance|all]
rclonectl enable [instance|all]
rclonectl disable [instance|all]
rclonectl log <instance>
rclonectl cache [instance|all]
rclonectl stats [instance|all]
rclonectl refresh <instance> [path] [true|false]
rclonectl forget <instance> [path]
rclonectl check [instance|all]
rclonectl version
rclonectl update [--dev|<version>]
rclonectl uninstall [--purge]
rclonectl help
```

---

## 6. 업데이트

```bash
# 최신 Stable
sudo rclonectl update

# 최신 개발버전(RC)
sudo rclonectl update --dev

# 특정 버전
sudo rclonectl update 0.1.0-rc.3
```

업데이트는 `/etc/rclone/*.env`, `*.filter`, `rclone.conf` 같은 사용자 설정을 변경하지 않습니다. 실행 중인 mount도 자동 재시작하지 않으므로 새 프로그램 설정을 실행 중 서비스에 적용하려면 필요할 때 직접 재시작합니다.

```bash
sudo rclonectl restart all
```

---

## 7. Filter

인스턴스별 filter 파일은 다음 위치를 사용합니다.

```text
/etc/rclone/<instance>.filter
```

주석과 빈 줄만 있으면 filter를 적용하지 않습니다. 실제 규칙이 하나 이상 있을 때만 `--filter-from`이 활성화됩니다.

---

## 8. 제거

### rclone-manager만 제거

```bash
sudo rclonectl uninstall
```

기본 제거에서는 `/etc/rclone`의 사용자 설정을 보존합니다. rclone 프로그램 자체도 제거하지 않습니다.

설정까지 제거하려는 경우:

```bash
sudo rclonectl uninstall --purge
```

`--purge` 사용 전 필요한 `rclone.conf`, `.env`, `.filter`를 반드시 확인합니다. mount 경로와 VFS cache 디렉터리는 자동 삭제하지 않습니다.

### rclone 자체 제거

먼저 실제 실행 파일 위치를 확인합니다.

```bash
command -v rclone
```

공식 설치 스크립트 또는 wiserain Mod 설치 스크립트로 `/usr/bin/rclone`에 설치했고 더 이상 rclone을 사용하지 않는 것이 확실한 경우:

```bash
sudo rm -f /usr/bin/rclone
```

패키지 관리자(`apt`, `dnf`, `yum` 등)로 설치했다면 파일을 직접 삭제하지 말고 해당 패키지 관리자의 제거 명령을 사용합니다. rclone 실행 파일 제거와 `rclone.conf`, cache, mount 경로 삭제는 별개의 작업입니다.

---

## 9. 기본 운영 예

```bash
rclone version
rclone listremotes

sudo rclonectl create media
sudo vi /etc/rclone/media.env
sudo vi /etc/rclone/media.filter
sudo rclonectl check media
sudo rclonectl enable media
sudo rclonectl start media
rclonectl status media
```

문제가 있을 때:

```bash
rclonectl status media
rclonectl log media
sudo rclonectl check media
```
