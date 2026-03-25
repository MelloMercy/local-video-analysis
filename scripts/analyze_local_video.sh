#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: analyze_local_video.sh <video_path> [interval_seconds]" >&2
  exit 1
fi

VIDEO_PATH="$1"
INTERVAL="${2:-30}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_DIR="${LVA_RUNS_DIR:-$PROJECT_ROOT/runs}"
NAME="$(basename "$VIDEO_PATH")"
STEM="${NAME%.*}"
OUT_DIR="$BASE_DIR/$STEM"
FRAMES_DIR="$OUT_DIR/frames"
AUDIO_PATH="$OUT_DIR/audio.m4a"
PROMPT_FILE="${LVA_PROMPT_FILE:-$PROJECT_ROOT/docs/tech-glossary.txt}"
mkdir -p "$FRAMES_DIR"

echo "[1/4] probe video"
python3 "$SCRIPT_DIR/video_probe.py" "$VIDEO_PATH" > "$OUT_DIR/probe.json"

echo "[2/4] extract frames"
swift "$SCRIPT_DIR/extract_frames.swift" "$VIDEO_PATH" "$FRAMES_DIR" "$INTERVAL" > "$OUT_DIR/frames.txt"

echo "[3/4] export audio"
swift "$SCRIPT_DIR/export_audio.swift" "$VIDEO_PATH" "$AUDIO_PATH" > "$OUT_DIR/audio_path.txt"

echo "[4/4] transcribe audio"
python3 "$SCRIPT_DIR/transcribe_audio.py" \
  "$AUDIO_PATH" \
  --model mlx-community/whisper-large-v3-turbo \
  --prompt-file "$PROMPT_FILE" \
  --prompt-mode auto \
  --output-dir "$OUT_DIR" \
  --output-name transcript > "$OUT_DIR/transcribe_result.json"

PRECISE_DIR="$OUT_DIR/precise"
mkdir -p "$PRECISE_DIR"

echo "[extra] build precise transcript"
python3 "$SCRIPT_DIR/build_precise_transcript.py" \
  "$AUDIO_PATH" \
  --out-dir "$PRECISE_DIR" \
  --prompt-file "$PROMPT_FILE" > "$OUT_DIR/precise_result.json"

cat <<EOF
Done.
Run directory: $OUT_DIR
Probe: $OUT_DIR/probe.json
Frames: $FRAMES_DIR
Audio: $AUDIO_PATH
Transcript raw: $OUT_DIR/transcript.json
Transcript text: $OUT_DIR/transcript.txt
Transcript clean md: $OUT_DIR/transcript.clean.md
Transcript timeline md: $OUT_DIR/transcript.timeline.md
Precise transcript clean md: $PRECISE_DIR/precise_transcript.clean.md
Precise transcript timeline md: $PRECISE_DIR/precise_transcript.timeline.md
Precise suspicious review: $PRECISE_DIR/suspicious_segments.md

Next step:
- Analyze frames and merge precise transcript + visuals into a report.
EOF
