#!/usr/bin/env bash
set -Eeuo pipefail
readonly HUB_REPOSITORY="${RELEASE_HUB_REPOSITORY:-jejusee/releases}"
readonly HUB_BRANCH="${RELEASE_HUB_BRANCH:-main}"
TEMP_DIR=""
cleanup(){ [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]] && rm -rf -- "$TEMP_DIR"; }
trap cleanup EXIT
log(){ printf '[release-hub] %s\n' "$*"; }
die(){ printf '[release-hub] ERROR: %s\n' "$*" >&2; exit 1; }
command_exists(){ command -v "$1" >/dev/null 2>&1; }
download(){ local url="$1" out="$2"; if command_exists curl; then curl -fL --silent --show-error --retry 3 --connect-timeout 15 -o "$out" "$url"; elif command_exists wget; then wget -q --tries=3 --timeout=15 -O "$out" "$url"; else die "curl or wget is required."; fi; }
sha256_file(){ if command_exists sha256sum; then sha256sum "$1" | awk '{print $1}'; elif command_exists shasum; then shasum -a 256 "$1" | awk '{print $1}'; else die "sha256sum or shasum is required."; fi; }
platform_key(){ local os arch; case "$(uname -s)" in Linux) os=linux;; Darwin) os=macos;; *) die "Unsupported operating system: $(uname -s)";; esac; case "$(uname -m)" in x86_64|amd64) arch=x64;; aarch64|arm64) arch=arm64;; *) die "Unsupported architecture: $(uname -m)";; esac; printf '%s-%s\n' "$os" "$arch"; }
json_asset(){
  local manifest="$1" version="$2" platform="$3"
  if command_exists python3; then
    python3 - "$manifest" "$version" "$platform" <<'PYJSON'
import json,sys
m=json.load(open(sys.argv[1], encoding='utf-8')); version=sys.argv[2]; platform=sys.argv[3]
entry=m.get('stable') if not version else (m.get('versions') or {}).get(version)
if not entry: raise SystemExit(2)
a=(entry.get('assets') or {}).get(platform) or (entry.get('assets') or {}).get('any')
if not a: raise SystemExit(3)
print(entry['version']); print(a['url']); print(a['sha256']); print(a.get('type','archive')); print(a.get('installer',''))
PYJSON
  elif command_exists jq; then
    local q entry
    if [[ -z "$version" ]]; then q='.stable'; else q=".versions[\"$version\"]"; fi
    entry="$(jq -cer "$q" "$manifest")" || return 2
    jq -er --arg p "$platform" '[.version, ((.assets[$p] // .assets.any).url), ((.assets[$p] // .assets.any).sha256), ((.assets[$p] // .assets.any).type // "archive"), ((.assets[$p] // .assets.any).installer // "")] | .[]' <<<"$entry"
  else die "python3 or jq is required to read release metadata."; fi
}
extract_archive(){ local archive="$1" dest="$2" url="$3"; mkdir -p "$dest"; case "$url" in *.tar.gz|*.tgz) tar -xzf "$archive" -C "$dest";; *.tar.xz) tar -xJf "$archive" -C "$dest";; *.zip) command_exists unzip || die "unzip is required for ZIP packages."; unzip -q "$archive" -d "$dest";; *) die "Unsupported archive format: $url";; esac; }
find_package_root(){ local d="$1" installer="$2"; [[ -f "$d/VERSION" && -f "$d/$installer" ]] && { printf '%s\n' "$d"; return; }; local c; for c in "$d"/*; do [[ -d "$c" && -f "$c/VERSION" && -f "$c/$installer" ]] && { printf '%s\n' "$c"; return; }; done; return 1; }
main(){
  (( $# >= 1 && $# <= 2 )) || die "Usage: install.sh <project> [version]"
  local project="$1" requested="${2:-}" platform manifest meta version url expected type installer archive actual extract root
  [[ "$project" =~ ^[a-z0-9][a-z0-9._-]*$ ]] || die "Invalid project: $project"
  requested="${requested#v}"; platform="$(platform_key)"; TEMP_DIR="$(mktemp -d -t release-hub.XXXXXXXX)"
  manifest="$TEMP_DIR/manifest.json"
  download "https://raw.githubusercontent.com/${HUB_REPOSITORY}/${HUB_BRANCH}/${project}/manifest.json" "$manifest"
  if ! meta="$(json_asset "$manifest" "$requested" "$platform")"; then die "No matching release for ${project} (${requested:-stable}, ${platform})."; fi
  version="$(printf '%s\n' "$meta" | sed -n '1p')"; url="$(printf '%s\n' "$meta" | sed -n '2p')"; expected="$(printf '%s\n' "$meta" | sed -n '3p')"; type="$(printf '%s\n' "$meta" | sed -n '4p')"; installer="$(printf '%s\n' "$meta" | sed -n '5p')"
  [[ "$expected" =~ ^[A-Fa-f0-9]{64}$ ]] || die "Invalid SHA256 metadata."
  archive="$TEMP_DIR/asset"; log "Installing ${project} ${version} (${platform})"; download "$url" "$archive"
  actual="$(sha256_file "$archive")"; [[ "${actual,,}" == "${expected,,}" ]] || die "SHA256 verification failed."
  case "$type" in
    archive)
      [[ -n "$installer" ]] || die "Archive asset has no installer metadata."
      [[ "$installer" != /* && "$installer" != *'..'* ]] || die "Unsafe installer path."
      extract="$TEMP_DIR/package"; extract_archive "$archive" "$extract" "$url"
      root="$(find_package_root "$extract" "$installer")" || die "Invalid release package."
      [[ "$(head -n1 "$root/VERSION")" == "$version" ]] || die "Package version mismatch."
      bash "$root/$installer"
      ;;
    executable)
      chmod 0700 "$archive"; "$archive";;
    *) die "Unsupported asset type for shell bootstrap: $type";;
  esac
}
main "$@"
