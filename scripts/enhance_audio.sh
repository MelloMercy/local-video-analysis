#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: enhance_audio.sh <input_audio> <output_audio>" >&2
  exit 1
fi

IN="$1"
OUT="$2"
mkdir -p "$(dirname "$OUT")"

ffmpeg -y -i "$IN" \
  -vn \
  -ac 1 \
  -ar 16000 \
  -af "highpass=f=120,lowpass=f=7600,afftdn,loudnorm" \
  "$OUT"

echo "$OUT"
