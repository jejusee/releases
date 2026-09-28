# Release Hub

공용 배포 허브입니다. 프로젝트 소스 저장소는 빌드/패키징만 담당하고, 이 저장소가 버전 계산, GitHub Release, SHA256, manifest와 bootstrap을 공통 관리합니다.

## 고정 인터페이스

- `<project>/manifest.json`: 프로젝트별 배포 인덱스
- `<project>/install.sh`: Linux/macOS용 얇은 설치 진입점(선택)
- `bootstrap/install.sh`: 공통 Shell bootstrap 엔진
- `.github/workflows/plan.yml`: 다음 버전 계산
- `.github/workflows/publish.yml`: Release + manifest 게시

## 버전 흐름

`patch/minor/major`는 새 `-rc.1`, `beta`는 RC 증가, `release`는 현재 RC를 stable로 승격합니다.

## Asset spec

```json
[{"platform":"linux-x64","file":"app-1.0.0-linux-x64.tar.gz","type":"archive","installer":"lib/install.sh"}]
```

`platform`은 프로젝트가 자유롭게 정의하며 bootstrap 기본키는 `linux-x64`, `linux-arm64`, `macos-x64`, `macos-arm64`입니다. `any` fallback도 사용할 수 있습니다. `type`은 `archive`, `executable`, `msi`를 manifest 규약에서 허용합니다. Shell bootstrap은 `archive`와 `executable`을 처리합니다. Windows용 공통 bootstrap은 별도 PowerShell 엔진을 추가할 수 있으며 manifest 규약은 그대로 유지됩니다.

## 새 프로젝트 추가

1. `<project>/manifest.json` 생성
2. 필요하면 `<project>/install.sh` 같은 얇은 wrapper 생성
3. dev 저장소의 Release workflow에서 `plan.yml` → build/package → `publish.yml` 호출

Release Hub 엔진은 프로젝트별로 복사하지 않습니다. 검증 후 caller는 `@main` 대신 고정 태그(예: `@hub-v1`)에 pin하는 것을 권장합니다.
