# rclone-manager

`rclone-manager`는 Linux 서버의 rclone mount 인스턴스를 systemd와 `rclonectl`로 관리하기 위한 프로젝트입니다.

이 저장소(`rclone-manager-dev`)는 **개발용 Private Repository**입니다. 실제 배포 파일과 manifest는 Public Release Hub인 `jejusee/releases`에서 관리합니다.

---

## 1. 가장 먼저: Git으로 프로젝트 받기

앞으로는 GitHub에서 ZIP을 내려받아 수정하거나 웹의 **Upload files**로 덮어쓰지 않는 것을 권장합니다.

Git을 사용하면 `.github`, `.gitignore`처럼 `.`으로 시작하는 파일과 폴더도 빠짐없이 관리됩니다.

### 1-1. Git for Windows 설치

Windows PC에 Git이 없다면 **Git for Windows**를 설치합니다.

설치 후 `명령 프롬프트(cmd)`에서 다음 명령이 동작하면 준비가 끝난 것입니다.

```bat
git --version
```

`git version ...`이 표시되면 정상입니다.

### 1-2. 저장소 Clone — 최초 1회만

프로젝트를 보관할 상위 폴더에서 명령 프롬프트를 열고 실행합니다.

```bat
git clone https://github.com/jejusee/rclone-manager-dev.git
```

Private Repository이므로 처음에는 GitHub 로그인이 요구될 수 있습니다. Git for Windows의 Git Credential Manager가 브라우저 로그인을 표시하면 사용하는 GitHub 계정으로 인증하면 됩니다.

완료되면 다음 폴더가 만들어집니다.

```text
rclone-manager-dev\
├─ .github\
├─ bin\
├─ config\
├─ lib\
├─ systemd\
├─ .gitignore
├─ dev.cmd
└─ README.md
```

> **중요:** GitHub에서 다운로드한 ZIP을 풀어 만든 폴더에서는 `dev.cmd`를 사용하지 마세요. 반드시 `git clone`으로 받은 폴더에서 사용합니다.

---

## 2. `dev.cmd` 사용법

프로젝트 루트의 **`dev.cmd`를 더블클릭**하면 Git 명령을 직접 입력하지 않고 대부분의 작업을 할 수 있습니다.

실행하면 다음 메뉴가 표시됩니다.

```text
[1] 현재 상태 확인

[2] 작업 시작 - GitHub 최신 내용 받기

[3] 작업 종료 - 변경사항 저장 + GitHub 올리기

[4] 변경내용 확인
[5] 최근 Commit 확인
[6] GitHub Repository 열기
[7] 프로젝트 ZIP 백업

[0] 종료
```

평소에는 **2번 → 파일 작업 → 3번**만 기억하면 됩니다.

```text
작업 시작
   ↓
dev.cmd → [2]
   ↓
파일 수정 / 새 파일 복사 / ChatGPT 결과물 덮어쓰기
   ↓
dev.cmd → [3]
   ↓
Commit 메시지 입력
   ↓
GitHub 저장 완료
```

---

## 3. 평소 작업 방법

### 작업을 시작할 때 — `[2]`

`dev.cmd`를 실행하고:

```text
[2] 작업 시작 - GitHub 최신 내용 받기
```

를 선택합니다.

이 기능은 GitHub의 최신 변경사항을 현재 PC로 가져옵니다.

내부적으로 안전한 `fetch`와 `pull --ff-only`만 사용하므로 로컬 파일을 강제로 삭제하거나 강제 병합하지 않습니다.

성공하면 다음과 같이 생각하면 됩니다.

```text
GitHub 최신본 → 내 PC
```

회사 PC와 집 PC처럼 여러 컴퓨터에서 작업한다면 **작업을 시작하기 전에 항상 2번을 먼저 실행**하는 것이 좋습니다.

### 파일 수정

이제 Visual Studio, VS Code 또는 일반 편집기로 파일을 수정합니다.

ChatGPT에서 새 프로젝트 ZIP을 받은 경우에도 **GitHub 웹에 업로드하지 말고**, ZIP의 내용을 이 Clone 폴더에 그대로 복사하여 덮어쓰면 됩니다.

예:

```text
다운로드한 새 버전 ZIP
        ↓ 압축 해제
.github\             ┐
bin\                 │
config\              │
lib\                 ├─→ rclone-manager-dev\ 에 복사/덮어쓰기
systemd\             │
README.md             │
dev.cmd               ┘
```

이 방법이면 `.github/workflows/release.yml`이나 `.gitignore`도 Git이 정상적으로 변경사항으로 인식합니다.

> `.git` 폴더는 Clone한 저장소의 Git 정보이므로 삭제하거나 다른 ZIP의 파일로 교체하지 않습니다. 배포용 ZIP에는 `.git` 폴더가 없어야 정상입니다.

### 작업이 끝났을 때 — `[3]`

다시 `dev.cmd`를 실행하고:

```text
[3] 작업 종료 - 변경사항 저장 + GitHub 올리기
```

를 선택합니다.

현재 변경 파일을 확인한 뒤 Commit 메시지를 입력합니다.

예:

```text
Release Hub operation naming 적용
```

또는:

```text
mount filter 처리 개선
```

그러면 `dev.cmd`가 변경사항을 Commit하고 GitHub에 Push합니다.

```text
내 PC 변경사항 → GitHub
```

정상적으로 끝났다면 GitHub 웹에서도 변경된 파일을 확인할 수 있습니다.

---

## 4. 메뉴별 기능

### `[1] 현재 상태 확인`

현재 Git 상태를 보여줍니다.

파일을 수정했는지, 새 파일이 있는지, Commit되지 않은 내용이 있는지 확인할 때 사용합니다.

### `[2] 작업 시작 - GitHub 최신 내용 받기`

GitHub의 최신 내용을 현재 PC로 가져옵니다.

로컬에 아직 저장하지 않은 변경사항이 있으면 안전을 위해 Pull을 중단합니다. 이 경우 먼저 변경사항을 확인하고 필요하면 `[3]`으로 GitHub에 저장한 후 다시 실행합니다.

### `[3] 작업 종료 - 변경사항 저장 + GitHub 올리기`

현재 프로젝트의 변경사항을 Git에 추가하고 Commit한 뒤 GitHub로 Push합니다.

일상적으로 가장 많이 사용하는 메뉴입니다.

### `[4] 변경내용 확인`

Commit하기 전에 실제 변경 내용을 확인할 때 사용합니다.

`README.md`, shell script, workflow 등의 어느 부분이 바뀌었는지 확인하는 용도입니다.

### `[5] 최근 Commit 확인`

최근 저장 이력을 확인합니다.

어떤 작업을 언제 Commit했는지 확인할 때 사용합니다.

### `[6] GitHub Repository 열기`

현재 프로젝트의 `origin` 주소를 이용해 GitHub Repository를 브라우저에서 엽니다.

Repository 주소를 `dev.cmd`에 하드코딩하지 않으므로 다른 프로젝트에서도 재사용할 수 있습니다.

### `[7] 프로젝트 ZIP 백업`

현재 프로젝트를 ZIP으로 백업합니다.

백업은 프로젝트 아래 `_backup` 폴더에 생성됩니다.

```text
_backup\
└─ rclone-manager-dev-YYYYMMDD-HHMMSS.zip
```

`.git`과 기존 `_backup`은 백업 ZIP에서 제외됩니다.

이 기능은 GitHub Push를 대신하는 기능이 아니라 **별도의 로컬 스냅샷** 용도입니다.

---

## 5. 여러 PC에서 사용할 때

예를 들어 회사 PC와 집 PC에서 같은 프로젝트를 작업한다면 다음 순서를 지킵니다.

```text
회사 PC
  dev.cmd [2]
      ↓
  작업
      ↓
  dev.cmd [3]
      ↓
    GitHub
      ↓
집 PC
  dev.cmd [2]
      ↓
  작업
      ↓
  dev.cmd [3]
```

핵심은 **작업 전 `[2]`, 작업 후 `[3]`**입니다.

한 PC에서 작업한 내용을 `[3]`으로 Push하지 않은 상태에서 다른 PC에서 같은 파일을 수정하면 충돌이 생길 수 있습니다.

---

## 6. ChatGPT에서 수정본 ZIP을 받았을 때

앞으로 프로젝트 수정본을 ZIP으로 받은 경우 다음 순서로 적용하면 됩니다.

```text
1. rclone-manager-dev\dev.cmd 실행
2. [2] 작업 시작 선택
3. 받은 ZIP을 별도 임시 폴더에 압축 해제
4. 압축 해제한 파일/폴더 전체를 rclone-manager-dev\에 복사
5. 같은 이름의 파일은 덮어쓰기
6. rclone-manager-dev\dev.cmd 실행
7. [4] 변경내용 확인
8. [3] 작업 종료 선택
9. Commit 메시지 입력
10. GitHub Push 완료
```

이 방식의 장점은 GitHub 웹 업로드에서 놓치기 쉬운 다음 항목까지 Git이 정확하게 처리한다는 점입니다.

```text
.github/
.github/workflows/
.gitignore
```

또한 파일이 **추가된 경우뿐 아니라 수정되거나 삭제된 경우도 Git이 추적**합니다.

---

## 7. 현재 Release 작업

GitHub Actions의 **Version & Release** workflow에서 배포 작업을 선택합니다.

```text
[개발] Major  · 대규모 변경 버전 시작
[개발] Minor  · 기능 추가 버전 시작
[개발] Patch  · 버그 수정 버전 시작
[개발] RC     · 테스트 버전 업데이트
[배포] Stable · 정식 버전 출시
```

Release Hub 내부 operation은 다음과 같이 통일되어 있습니다.

```text
dev-major
dev-minor
dev-patch
dev-rc
release-stable
```

일반적인 Minor 개발 예시는 다음과 같습니다.

```text
현재 Stable 1.2.3
      ↓
[개발] Minor
      ↓
1.3.0-rc.1
      ↓
수정 후 [개발] RC
      ↓
1.3.0-rc.2
      ↓
테스트 완료
      ↓
[배포] Stable
      ↓
1.3.0
```

---

## 8. 배포 서버에서 설치·업데이트

### 8-1. 사전 준비: rclone 설치

`rclone-manager`는 rclone 자체를 포함하거나 대신 설치하지 않습니다. 먼저 서버에 **rclone을 설치하고 remote 설정을 완료**해야 합니다.

Linux에서는 rclone 공식 설치 스크립트를 사용하는 방법을 권장합니다.

```bash
sudo -v
curl https://rclone.org/install.sh | sudo bash
```

설치 후 버전을 확인합니다.

```bash
rclone version
```

이미 rclone이 설치되어 있다면 다시 설치할 필요는 없습니다. 최신 버전으로 갱신하려면 rclone 자체 업데이트 기능도 사용할 수 있습니다.

```bash
sudo rclone selfupdate
```

> `rclone-manager`의 `update` 명령은 **rclone-manager 자체를 업데이트**하는 명령입니다. rclone 프로그램 자체의 업데이트와는 별개입니다.

#### remote 설정

rclone을 처음 사용하는 서버라면 remote를 생성합니다.

```bash
rclone config
```

설정한 remote가 정상적으로 보이는지 확인합니다.

```bash
rclone listremotes
```

예를 들어 `gdm:`이라는 remote를 만들었다면 이후 인스턴스의 `REMOTE_PATH`에 다음과 같이 사용할 수 있습니다.

```ini
REMOTE_PATH=gdm:
```

`rclone-manager`는 시스템 서비스로 실행되므로 rclone 설정은 최종적으로 `/etc/rclone/rclone.conf`를 사용합니다. 기존 사용자 계정에서 만든 `rclone.conf`를 사용할 경우 필요한 remote 설정을 이 파일에 준비한 뒤 `rclonectl check`로 확인합니다.

#### rclone 제거

`rclone-manager`를 제거해도 rclone 자체는 자동으로 제거하지 않습니다. 다른 작업에서 rclone을 사용하고 있을 수 있기 때문입니다.

rclone을 더 이상 사용하지 않는 것이 확실한 경우에만 별도로 제거합니다. 공식 설치 스크립트로 설치한 Linux 환경에서는 먼저 실제 실행 파일 위치를 확인합니다.

```bash
command -v rclone
```

예를 들어 `/usr/bin/rclone`에 설치되어 있다면 바이너리를 제거할 수 있습니다.

```bash
sudo rm -f /usr/bin/rclone
```

패키지 관리자(`apt`, `dnf`, `yum` 등)로 설치했다면 파일을 직접 삭제하지 말고 **해당 패키지 관리자의 제거 명령**을 사용합니다.

> 주의: rclone 실행 파일을 제거하는 것과 `rclone.conf`, VFS cache, mount 경로를 삭제하는 것은 별개의 작업입니다. 설정이나 데이터가 필요할 수 있으므로 자동으로 삭제하지 않는 것을 권장합니다.

rclone 공식 설치 및 최신 안내:
https://rclone.org/install/

### 8-2. rclone-manager 설치

배포 서버에서는 개발 저장소를 Clone하지 않고 Public Release Hub를 사용합니다.

```bash
# 최신 Stable 설치
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash

# 최신 개발버전(RC) 설치
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- --dev

# 특정 버전 설치
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- 0.1.0-rc.3
```

설치 후 업데이트도 같은 규칙입니다.

```bash
sudo rclonectl update                 # 최신 Stable
sudo rclonectl update --dev           # 최신 개발버전(RC)
sudo rclonectl update 0.1.0-rc.3      # 정확한 지정 버전
```

Stable이 없으면 `update`가 RC를 자동 설치하지 않고 `--dev` 사용을 안내합니다.

기본 운영 흐름:

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

업데이트 후 mount는 자동 재시작하지 않습니다.

```bash
sudo rclonectl restart all
```

### 인스턴스 설정 원칙

`/etc/rclone/<instance>.env`는 모든 설정을 복사해 두는 파일이 아니라 **인스턴스별 override 파일**입니다.
기본적으로 다음 3개만 지정하면 됩니다.

```ini
REMOTE_PATH=gdm:
MOUNT_PATH=/mnt/gdm
RC_PORT=5572
```

그 밖의 설정은 생략하거나 주석 처리하면 rclone-manager의 권장 기본값을 자동으로 사용합니다.
특정 인스턴스에서 기본값을 바꿀 필요가 있을 때만 해당 항목의 주석을 해제하여 지정합니다.

```ini
# 기본값 사용
# BUFFER_SIZE=32M

# 이 인스턴스만 override
BUFFER_SIZE=64M
```

현재 자동 기본값은 다음과 같습니다.

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

`rclonectl create <instance>`로 생성되는 `.env` 예제에는 각 옵션의 설명과 기본값이 포함되어 있습니다. 기본값은 프로그램 버전에서 개선될 수 있으므로, 특별한 이유가 없다면 선택 설정을 불필요하게 고정하지 않는 것을 권장합니다.

상세 사용자 문서는 Public Release Hub의 `rclone-manager` 문서를 기준으로 합니다:
https://github.com/jejusee/releases/tree/main/rclone-manager

---

## 9. 프로젝트 구조

```text
rclone-manager-dev/
├─ .github/
│  └─ workflows/
│     └─ release.yml       # Release Hub 호출 workflow
├─ bin/
│  └─ rclonectl.sh         # 사용자 CLI
├─ config/
│  ├─ remote.env.example
│  └─ remote.filter.example
├─ lib/
│  ├─ common.sh
│  ├─ install.sh           # 배포 패키지 installer
│  ├─ mount.sh
│  ├─ uninstall.sh
│  └─ update.sh
├─ systemd/
│  └─ rclone@.service
├─ .gitignore
├─ dev.cmd                 # Windows 더블클릭 실행기
├─ dev.ps1                 # Windows Git 작업 도우미
└─ README.md
```

공개 bootstrap, 버전 계산, GitHub Release 생성 및 manifest 관리는 `jejusee/releases` Release Hub가 담당합니다.

---

## 10. 가장 간단한 사용법

Git 사용법을 모두 기억할 필요는 없습니다.

```text
┌─────────────────────────────────────┐
│ 작업 시작                           │
│ dev.cmd → 2                         │
│                                     │
│ 파일 수정                           │
│                                     │
│ 작업 종료                           │
│ dev.cmd → 3                         │
└─────────────────────────────────────┘
```

**`2 → 작업 → 3`**만 기본 습관으로 사용하면 됩니다.
