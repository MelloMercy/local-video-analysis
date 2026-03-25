#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: analyze_video.sh <video_path_or_url> [interval_seconds]" >&2
  exit 1
fi

SOURCE="$1"
INTERVAL="${2:-30}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_DIR="${LVA_RUNS_DIR:-$PROJECT_ROOT/runs}"
PROMPT_FILE="${LVA_PROMPT_FILE:-$PROJECT_ROOT/docs/tech-glossary.txt}"
mkdir -p "$BASE_DIR"

STEM="$(python3 - <<'PY' "$SOURCE"
import sys
from pathlib import Path
from urllib.parse import urlparse
src = sys.argv[1]
if src.startswith('http://') or src.startswith('https://'):
    p = urlparse(src)
    name = Path(p.path).name or 'remote_video'
    print(Path(name).stem or 'remote_video')
else:
    print(Path(src).expanduser().stem)
PY
)"
OUT_DIR="$BASE_DIR/$STEM"
SOURCE_DIR="$OUT_DIR/source"
mkdir -p "$SOURCE_DIR"

echo "[0/5] resolve source"
python3 "$SCRIPT_DIR/fetch_video.py" "$SOURCE" --output-dir "$SOURCE_DIR" > "$OUT_DIR/source_result.json"
VIDEO_PATH="$(python3 - <<'PY' "$OUT_DIR/source_result.json"
import json,sys
print(json.load(open(sys.argv[1]))['video_path'])
PY
)"
FRAMES_DIR="$OUT_DIR/frames"
AUDIO_PATH="$OUT_DIR/audio.m4a"
mkdir -p "$FRAMES_DIR"

echo "[1/5] probe video"
python3 "$SCRIPT_DIR/video_probe.py" "$VIDEO_PATH" > "$OUT_DIR/probe.json"

echo "[2/5] extract frames"
swift "$SCRIPT_DIR/extract_frames.swift" "$VIDEO_PATH" "$FRAMES_DIR" "$INTERVAL" > "$OUT_DIR/frames.txt"

echo "[3/5] export audio"
swift "$SCRIPT_DIR/export_audio.swift" "$VIDEO_PATH" "$AUDIO_PATH" > "$OUT_DIR/audio_path.txt"

echo "[4/5] transcribe audio"
python3 "$SCRIPT_DIR/transcribe_audio.py" \
  "$AUDIO_PATH" \
  --model mlx-community/whisper-large-v3-turbo \
  --prompt-file "$PROMPT_FILE" \
  --prompt-mode auto \
  --output-dir "$OUT_DIR" \
  --output-name transcript > "$OUT_DIR/transcribe_result.json"

PRECISE_DIR="$OUT_DIR/precise"
mkdir -p "$PRECISE_DIR"

echo "[5/5] build precise transcript"
python3 "$SCRIPT_DIR/build_precise_transcript.py" \
  "$AUDIO_PATH" \
  --out-dir "$PRECISE_DIR" \
  --prompt-file "$PROMPT_FILE" > "$OUT_DIR/precise_result.json"

cat <<EOF
Done.
Source input: $SOURCE
Resolved video: $VIDEO_PATH
Run directory: $OUT_DIR
Probe: $OUT_DIR/probe.json
Frames: $FRAMES_DIR
Audio: $AUDIO_PATH
Transcript clean md: $OUT_DIR/transcript.clean.md
Transcript timeline md: $OUT_DIR/transcript.timeline.md
Precise transcript clean md: $PRECISE_DIR/precise_transcript.clean.md
Precise transcript timeline md: $PRECISE_DIR/precise_transcript.timeline.md
Precise suspicious review: $PRECISE_DIR/suspicious_segments.md
EOF
