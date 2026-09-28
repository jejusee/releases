# rclone-manager

Linux 서버에서 여러 `rclone mount`를 인스턴스별로 관리하기 위한 도구입니다. systemd 기반으로 시작·중지·재시작·자동 시작을 관리하고 VFS Cache, 상태 확인, 업데이트와 제거 기능을 제공합니다.

## 1. 요구사항

- Linux
- systemd
- rclone
```
# 포크버전
curl -fsSL "https://raw.githubusercontent.com/wiserain/rclone/mod/install.sh" | sudo bash
#curl -fsSL "https://raw.githubusercontent.com/wiserain/rclone/mod/install.sh" | sudo bash -s v1.69.3-241
```
- FUSE (`fusermount3` 또는 `fusermount`)
- `curl` 또는 `wget`

설치 프로그램은 root 권한으로 실행합니다.

## 2. 설치

Stable 최신 버전 설치:

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash
```

`curl`이 없다면:

```bash
wget -qO- https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash
```

특정 버전 설치:

```bash
curl -fsSL https://raw.githubusercontent.com/jejusee/releases/main/rclone-manager/install.sh | sudo bash -s -- 0.1.0-rc.1
```

설치 확인:

```bash
rclonectl version
rclonectl help
```

> 현재 manifest에 Stable 버전이 아직 등록되지 않은 경우 Stable 설치 명령은 사용할 수 없습니다. 이 경우 배포된 특정 버전을 명시하여 설치합니다.

## 3. rclone Remote 준비

기본 rclone 설정 파일은 다음 위치를 사용합니다.

```text
/etc/rclone/rclone.conf
```

새 Remote를 구성하려면:

```bash
sudo rclone config --config /etc/rclone/rclone.conf
```

등록된 Remote 확인:

```bash
rclone listremotes --config /etc/rclone/rclone.conf
```

## 4. 첫 Mount 인스턴스 만들기

`/etc/rclone/<이름>.env` 파일 하나가 하나의 mount 인스턴스입니다.

예를 들어 `media` 인스턴스를 만듭니다.

```bash
sudo cp /etc/rclone/remote.env.example /etc/rclone/media.env
sudo nano /etc/rclone/media.env
```

주요 설정 예:

```ini
REMOTE_PATH=remote:
MOUNT_PATH=/mnt/media
CACHE_DIR=/var/cache/rclone/media
RC_PORT=5572
READ_ONLY=true
```

`REMOTE_PATH`는 `rclone.conf`에 등록한 Remote 이름에 맞게 변경합니다.

설정 파일 권한:

```bash
sudo chown root:root /etc/rclone/media.env
sudo chmod 600 /etc/rclone/media.env
```

여러 인스턴스를 만들 때는 각 인스턴스의 `RC_PORT`를 서로 다르게 지정해야 합니다.

## 5. 설정 검사와 시작

인스턴스 목록:

```bash
rclonectl list
```

설정 검사:

```bash
sudo rclonectl check media
```

모든 인스턴스 검사:

```bash
sudo rclonectl check all
```

시작:

```bash
sudo rclonectl start media
```

상태 확인:

```bash
rclonectl status media
```

부팅 시 자동 시작:

```bash
sudo rclonectl enable media
```

## 6. 자주 사용하는 명령

```bash
rclonectl list
rclonectl status media
rclonectl status all

sudo rclonectl start media
sudo rclonectl stop media
sudo rclonectl restart media

sudo rclonectl enable media
sudo rclonectl disable media

rclonectl log media
rclonectl stats media
rclonectl cache media

rclonectl refresh media
rclonectl forget media

sudo rclonectl check media
sudo rclonectl check all

rclonectl version
```

전체 도움말:

```bash
rclonectl help
```

## 7. Read-only / Read-write

읽기 전용:

```ini
READ_ONLY=true
```

읽기/쓰기:

```ini
READ_ONLY=false
```

쓰기 가능한 인스턴스에서는 `VFS_WRITE_BACK`, `TRANSFERS` 등의 설정도 사용됩니다. 전체 기본값과 설명은 `/etc/rclone/remote.env.example`을 참고하세요.

## 8. 새로운 Mount 추가

예를 들어 `backup` 인스턴스를 추가하려면:

```bash
sudo cp /etc/rclone/remote.env.example /etc/rclone/backup.env
sudo nano /etc/rclone/backup.env
sudo chown root:root /etc/rclone/backup.env
sudo chmod 600 /etc/rclone/backup.env
sudo rclonectl check backup
sudo rclonectl enable backup
sudo rclonectl start backup
```

`MOUNT_PATH`, `CACHE_DIR`, `RC_PORT`는 다른 인스턴스와 중복되지 않게 설정합니다.

## 9. 업데이트

현재 버전:

```bash
rclonectl version
```

Stable 최신 버전으로 업데이트:

```bash
sudo rclonectl update
```

특정 버전으로 업데이트:

```bash
sudo rclonectl update 0.2.0-rc.1
```

업데이트 시 `/etc/rclone/rclone.conf`과 `/etc/rclone/*.env`는 유지됩니다. 실행 중인 mount는 자동으로 재시작하지 않습니다.

필요할 때 직접 재시작합니다.

```bash
sudo rclonectl restart all
```

## 10. 삭제

프로그램만 삭제하고 `/etc/rclone` 설정을 유지:

```bash
sudo rclonectl uninstall
```

설정까지 함께 제거:

```bash
sudo rclonectl uninstall --purge
```

`--purge`는 `rclone.conf`, `*.env`, `remote.env.example`을 제거합니다. `/etc/rclone` 안의 알 수 없는 다른 파일, mount 디렉터리 및 VFS Cache 디렉터리는 자동 삭제하지 않습니다.

일반적인 재설치 가능성을 고려하면 기본 `uninstall`을 사용하는 것이 편리합니다.

## 11. 문제 해결

서비스 상태:

```bash
systemctl status rclone@media
```

최근 로그:

```bash
journalctl -u rclone@media -n 100
```

실시간 로그:

```bash
journalctl -u rclone@media -f
```

mount 확인:

```bash
findmnt /mnt/media
mountpoint /mnt/media
```

rclone Remote 확인:

```bash
rclone listremotes --config /etc/rclone/rclone.conf
```

설정 재검사:

```bash
sudo rclonectl check media
```

## 12. 주요 파일 위치

```text
/usr/local/bin/rclonectl
/usr/local/lib/rclone-manager/
/etc/systemd/system/rclone@.service

/etc/rclone/rclone.conf
/etc/rclone/remote.env.example
/etc/rclone/*.env
```

프로그램을 제거하더라도 기본 `uninstall`에서는 `/etc/rclone`의 사용자 설정을 보존합니다.
