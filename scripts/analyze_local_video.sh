#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo "usage: analyze_local_video.sh <video_path> [interval_seconds]" >&2
  echo "note: analyze_local_video.sh is kept for backward compatibility; prefer analyze_video.sh" >&2
  exit 1
fi

exec bash "$SCRIPT_DIR/analyze_video.sh" "$@"
