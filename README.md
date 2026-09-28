# Releases

여러 소프트웨어 프로젝트의 **공통 Public 배포 저장소**입니다.

개발 소스는 각 프로젝트의 별도 Private 저장소에서 관리하고, 이 저장소에는 사용자가 설치와 업데이트에 필요한 공개 파일 및 프로젝트별 사용 설명서를 제공합니다.

## Projects

| Project | Description | Documentation |
|---|---|---|
| `rclone-manager` | Linux rclone mount 관리 도구 | [사용 설명서](rclone-manager/README.md) |

새 프로젝트는 프로젝트 이름의 폴더를 하나 추가하여 동일한 구조로 관리합니다.

## Repository 구조

```text
releases/
├── README.md
├── rclone-manager/
│   ├── README.md
│   ├── install.sh
│   └── manifest.json
└── <project>/
    ├── README.md
    ├── install.*
    └── manifest.json
```

각 프로젝트 폴더는 하나의 독립된 배포 단위입니다.

- `README.md` — 해당 프로젝트의 설치, 설정, 사용, 업데이트, 삭제 및 문제 해결 설명
- `install.*` — 최초 설치를 위한 Bootstrap installer
- `manifest.json` — Stable/Prerelease 버전, 다운로드 주소 및 SHA256 정보

실제 `.tar.gz`, `.zip`, `.exe` 등의 프로그램 패키지는 Git 저장소에 직접 넣지 않고 **GitHub Release Assets**로 배포합니다.

## 배포 흐름

```text
Private Development Repository
        ↓
GitHub Actions
        ↓
GitHub Release Assets
        ↓
프로젝트별 manifest.json 갱신
        ↓
사용자 설치 / 업데이트
```

Release 버전이 변경될 때마다 이 README를 수정할 필요는 없습니다. 프로젝트가 추가되거나 공통 배포 구조가 변경될 때만 갱신합니다.
