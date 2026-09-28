#!/usr/bin/env bash
set -Eeuo pipefail
readonly PROJECT="rclone-manager"
readonly RELEASE_REPO="jejusee/releases"
readonly MANIFEST_URL="https://raw.githubusercontent.com/${RELEASE_REPO}/main/${PROJECT}/manifest.json"
readonly PLATFORM="linux-x64"
TEMP_DIR=""
cleanup(){ [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]] && rm -rf -- "$TEMP_DIR"; }
trap cleanup EXIT
log(){ printf '[rclone-manager] %s\n' "$*"; }
die(){ printf '[rclone-manager] ERROR: %s\n' "$*" >&2; exit 1; }
download(){ local url="$1" out="$2"; if command -v curl >/dev/null 2>&1; then curl -fL --silent --show-error --retry 3 --connect-timeout 15 -o "$out" "$url"; elif command -v wget >/dev/null 2>&1; then wget -q --tries=3 --timeout=15 -O "$out" "$url"; else die "curl or wget is required."; fi; }
normalize_version(){ local v="${1#v}"; [[ "$v" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-rc\.[0-9]+)?$ ]] || die "Invalid version: $v"; printf '%s\n' "$v"; }
json_value(){
    local file="$1" expr="$2"
    if command -v jq >/dev/null 2>&1; then jq -er "$expr" "$file"
    elif command -v python3 >/dev/null 2>&1; then
        python3 - "$file" "$expr" <<'PYJSON'
import json,sys
obj=json.load(open(sys.argv[1], encoding='utf-8'))
for p in sys.argv[2].strip('.').split('.'):
    obj=obj[p]
if obj is None: raise SystemExit(1)
print(obj)
PYJSON
    else die "jq or python3 is required."; fi
}
sha256_file(){ if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'; else die "sha256sum or shasum is required."; fi; }
main(){
    [[ "$(uname -s)" == Linux ]] || die "Only Linux is supported."
    [[ "$EUID" -eq 0 ]] || die "Run this installer as root."
    (( $# <= 1 )) || die "Usage: install.sh [version]"
    command -v tar >/dev/null 2>&1 || die "tar is required."
    TEMP_DIR="$(mktemp -d -t rclone-manager-bootstrap.XXXXXXXX)"
    local manifest="$TEMP_DIR/manifest.json" requested="${1:-}" version url expected archive actual extract root
    download "$MANIFEST_URL" "$manifest"
    if [[ -z "$requested" ]]; then
        version="$(normalize_version "$(json_value "$manifest" '.stable.version' 2>/dev/null || die 'No stable release is currently published.')")"
        url="$(json_value "$manifest" ".stable.assets.${PLATFORM}.url")"
        expected="$(json_value "$manifest" ".stable.assets.${PLATFORM}.sha256")"
    else
        version="$(normalize_version "$requested")"
        url="$(json_value "$manifest" ".versions.${version}.assets.${PLATFORM}.url" 2>/dev/null)" || die "Version not found: $version"
        expected="$(json_value "$manifest" ".versions.${version}.assets.${PLATFORM}.sha256" 2>/dev/null)" || die "Checksum not found: $version"
    fi
    [[ "$expected" =~ ^[A-Fa-f0-9]{64}$ ]] || die "Invalid checksum metadata."
    archive="$TEMP_DIR/${PROJECT}-${version}.tar.gz"
    log "Installing version: $version"
    download "$url" "$archive"
    actual="$(sha256_file "$archive")"
    [[ "${actual,,}" == "${expected,,}" ]] || die "Checksum verification failed."
    extract="$TEMP_DIR/package"; mkdir -p "$extract"; tar -xzf "$archive" -C "$extract"
    root="$extract/${PROJECT}-${version}"
    [[ -f "$root/VERSION" && -f "$root/lib/install.sh" ]] || die "Invalid release package."
    [[ "$(head -n1 "$root/VERSION")" == "$version" ]] || die "Package version mismatch."
    bash "$root/lib/install.sh"
}
main "$@"
