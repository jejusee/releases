#!/usr/bin/env bash
set -Eeuo pipefail

readonly PROJECT="rclone-manager"
readonly RELEASE_REPO="jejusee/releases"
readonly MANIFEST_URL="https://raw.githubusercontent.com/${RELEASE_REPO}/main/manifests/${PROJECT}.json"
TEMP_DIR=""
cleanup(){ [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]] && rm -rf -- "$TEMP_DIR"; }
trap cleanup EXIT
log(){ printf '[rclone-manager] %s\n' "$*"; }
die(){ printf '[rclone-manager] ERROR: %s\n' "$*" >&2; exit 1; }
download(){ local u="$1" o="$2"; if command -v curl >/dev/null 2>&1; then curl -fL --silent --show-error --retry 3 --connect-timeout 15 -o "$o" "$u"; elif command -v wget >/dev/null 2>&1; then wget -q --tries=3 --timeout=15 -O "$o" "$u"; else die "curl or wget is required."; fi; }
normalize(){ local v="${1#v}"; [[ "$v" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z][0-9A-Za-z.-]*)?$ ]] || die "Invalid version: $v"; printf '%s\n' "$v"; }
json_value(){ local file="$1" expr="$2"; if command -v jq >/dev/null 2>&1; then jq -er "$expr" "$file"; elif command -v python3 >/dev/null 2>&1; then python3 - "$file" "$expr" <<'PY'
import json,sys
obj=json.load(open(sys.argv[1]))
parts=sys.argv[2].strip('.').split('.')
for p in parts: obj=obj[p]
if obj is None: raise SystemExit(1)
print(obj)
PY
else die "jq or python3 is required."; fi; }
sha256(){ if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'; else die "sha256sum or shasum is required."; fi; }
main(){
  [[ "$EUID" -eq 0 ]] || die "Run this installer as root."
  (( $# <= 1 )) || die "Usage: install.sh [version]"
  TEMP_DIR="$(mktemp -d -t rclone-manager-install.XXXXXXXX)"
  local manifest="$TEMP_DIR/manifest.json" version url expected archive root
  download "$MANIFEST_URL" "$manifest"
  if (( $# == 0 )); then
    version="$(json_value "$manifest" '.stable.version')"
    url="$(json_value "$manifest" '.stable.assets.linux.url')"
    expected="$(json_value "$manifest" '.stable.assets.linux.sha256')"
  else
    version="$(normalize "$1")"
    local tag="${PROJECT}-v${version}"
    url="https://github.com/${RELEASE_REPO}/releases/download/${tag}/${PROJECT}-${version}.tar.gz"
    local sums="$TEMP_DIR/SHA256SUMS"
    download "https://github.com/${RELEASE_REPO}/releases/download/${tag}/SHA256SUMS" "$sums"
    expected="$(awk -v f="${PROJECT}-${version}.tar.gz" '$2==f || $2=="*"f {print $1; exit}' "$sums")"
  fi
  version="$(normalize "$version")"
  [[ "$expected" =~ ^[A-Fa-f0-9]{64}$ ]] || die "Invalid checksum metadata."
  archive="$TEMP_DIR/${PROJECT}-${version}.tar.gz"
  log "Installing version: $version"
  download "$url" "$archive"
  [[ "$(sha256 "$archive")" == "${expected,,}" ]] || die "Package checksum verification failed."
  mkdir "$TEMP_DIR/package"; tar -xzf "$archive" -C "$TEMP_DIR/package"
  root="$TEMP_DIR/package/${PROJECT}-${version}"
  [[ -f "$root/install.sh" && -f "$root/VERSION" ]] || die "Invalid release package."
  [[ "$(head -n1 "$root/VERSION")" == "$version" ]] || die "Package version mismatch."
  bash "$root/install.sh"
  log "Installation completed: $version"
}
main "$@"
