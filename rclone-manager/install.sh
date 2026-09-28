#!/usr/bin/env bash
set -Eeuo pipefail
readonly BOOTSTRAP_URL="https://raw.githubusercontent.com/jejusee/releases/main/bootstrap/install.sh"
TMP="$(mktemp -t release-hub-bootstrap.XXXXXXXX)"; trap 'rm -f -- "$TMP"' EXIT
if command -v curl >/dev/null 2>&1; then curl -fL --silent --show-error --retry 3 --connect-timeout 15 -o "$TMP" "$BOOTSTRAP_URL"; elif command -v wget >/dev/null 2>&1; then wget -q --tries=3 --timeout=15 -O "$TMP" "$BOOTSTRAP_URL"; else echo 'curl or wget is required.' >&2; exit 1; fi
exec bash "$TMP" rclone-manager "$@"
