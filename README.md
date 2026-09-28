# Releases

개인 프로젝트의 설치 패키지와 업데이트 파일을 배포하기 위한 Public 저장소입니다.

각 프로젝트의 개발 소스는 별도의 Private 저장소에서 관리하며, 이 저장소는 **프로그램 배포와 사용자 문서 제공**을 목적으로 사용합니다.

## 사용 방법

사용하려는 프로젝트의 전용 문서를 확인하세요.

| Project | Description | Documentation |
|---|---|---|
| rclone-manager | Linux rclone mount 관리 도구 | [사용 설명서](docs/rclone-manager.md) |

각 프로젝트의 설치, 설정, 사용, 업데이트 및 삭제 방법은 해당 프로젝트의 전용 문서에서 제공합니다.

## Repository 구조

```text
releases/
├── README.md
├── docs/
│   ├── rclone-manager.md
│   └── ...
├── installers/
│   ├── rclone-manager.sh
│   └── ...
└── manifests/
    ├── rclone-manager.json
    └── ...
```

### `docs/`

프로젝트별 사용자 설명서를 저장합니다.

각 문서에는 해당 프로젝트의:

- 설치
- 초기 설정
- 사용 방법
- 업데이트
- 삭제
- 문제 해결

등 실제 사용에 필요한 내용을 제공합니다.

### `installers/`

프로젝트별 설치 프로그램을 제공합니다.

예:

```text
installers/rclone-manager.sh
```

설치 방법은 각 프로젝트의 `docs/` 문서를 참고하세요.

### `manifests/`

프로젝트별 배포 버전과 다운로드 정보를 관리합니다.

예:

```text
manifests/rclone-manager.json
```

Manifest는 설치 및 업데이트 프로그램이 현재 배포 버전과 Release Asset을 확인하기 위해 사용합니다.

일반 사용자가 직접 수정할 필요는 없습니다.

### GitHub Releases

실제 배포 패키지는 Git 저장소에 직접 저장하지 않고 GitHub Release Assets로 제공합니다.

예:

```text
rclone-manager-v0.1.0
└── rclone-manager-0.1.0.tar.gz
```

## Stable / Prerelease

프로젝트는 필요에 따라 Stable과 Prerelease 버전을 구분하여 배포할 수 있습니다.

```text
Stable
0.1.0
0.2.0

Prerelease
0.2.0-rc.1
0.2.0-rc.2
```

일반 설치 및 업데이트에서는 Stable 버전을 사용합니다.

Prerelease 버전은 테스트가 필요한 경우 명시적으로 선택하여 사용합니다.

## 배포 원칙

개발 소스와 배포 파일을 분리하여 관리합니다.

```text
Private Development Repository
        │
        │ GitHub Actions
        ▼
Public releases Repository
        │
        ├── Documentation
        ├── Installer
        ├── Manifest
        │
        ▼
GitHub Release Assets
```

새로운 버전이 배포되면 Manifest가 갱신되므로 **버전이 변경될 때마다 README를 수정할 필요는 없습니다.**

README 또는 `docs/` 문서는 설치 방법, 명령어, 설정 방법 등 **사용 방법 자체가 변경된 경우에만 갱신**합니다.
