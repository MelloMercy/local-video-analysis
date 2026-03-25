#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def find_bin(name: str, extra=None):
    extra = extra or []
    candidates = [shutil.which(name), *extra]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def ffprobe_duration(ffprobe_bin: str, audio: Path) -> float:
    out = run([ffprobe_bin, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(audio)])
    return float(out.stdout.strip())


def fmt_hms(seconds: float) -> str:
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def clean_text(text: str) -> str:
    replacements = {
        'Open 可老': 'OpenClaw', 'Open可能': 'OpenClaw', 'Obro': 'OpenClaw',
        '非书': 'Feishu', '輝殊': 'Feishu', 'Fishu': 'Feishu',
        'A晶': 'agent', '艾进': 'agent', 'Cescent Key': 'sessionKey',
        'Alorist': 'allowlist', 'Alorphone': 'allowFrom',
        'Portject Manager': 'project_manager', '全戰工人是': 'full_stack_engineer',
        '全程工人士': 'full_stack_engineer', '主艾進': '主 agent', '小脈': '小麦', 'APPC': 'App', '規程': 'Secret',
    }
    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)
    out = ' '.join(out.split())
    return out


def suspicious(text: str) -> bool:
    if not text.strip():
        return True
    bad_patterns = ['卖卖卖卖', '�', '����']
    if any(p in text for p in bad_patterns):
        return True
    # too much repetition of same char
    max_run = 1
    cur = 1
    for i in range(1, len(text)):
        if text[i] == text[i-1]:
            cur += 1
            max_run = max(max_run, cur)
        else:
            cur = 1
    return max_run >= 8


def load_prompt(path: Optional[Path]) -> Optional[str]:
    if not path:
        return None
    return path.read_text(encoding='utf-8').strip() or None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('audio_path')
    p.add_argument('--model', default='mlx-community/whisper-large-v3-turbo')
    p.add_argument('--language', default='zh')
    p.add_argument('--prompt-file')
    p.add_argument('--output-dir')
    p.add_argument('--segment-seconds', type=int, default=90)
    p.add_argument('--overlap-seconds', type=int, default=2)
    args = p.parse_args()

    audio = Path(args.audio_path).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else audio.parent / (audio.stem + '_segmented')
    out_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = find_bin('ffmpeg', ['/opt/homebrew/bin/ffmpeg'])
    ffprobe = find_bin('ffprobe', ['/opt/homebrew/bin/ffprobe'])
    mlx = find_bin('mlx_whisper', [str(Path.home() / 'Library' / 'Python' / '3.9' / 'bin' / 'mlx_whisper')])
    if not all([ffmpeg, ffprobe, mlx]):
        raise SystemExit('missing ffmpeg/ffprobe/mlx_whisper')

    prompt = load_prompt(Path(args.prompt_file).expanduser().resolve()) if args.prompt_file else None
    duration = ffprobe_duration(ffprobe, audio)
    seg = args.segment_seconds
    overlap = args.overlap_seconds
    starts = []
    t = 0
    while t < duration:
        starts.append(t)
        t += seg

    merged_segments = []
    chunks_meta = []
    for idx, start in enumerate(starts):
        chunk_start = max(0, start - (overlap if idx > 0 else 0))
        chunk_dur = min(seg + (overlap if idx > 0 else 0) + (overlap if start + seg < duration else 0), duration - chunk_start)
        chunk_audio = out_dir / f'chunk_{idx:03d}_{int(start):05d}s.m4a'
        run([ffmpeg, '-y', '-ss', str(chunk_start), '-t', str(chunk_dur), '-i', str(audio), '-vn', '-c:a', 'aac', '-b:a', '128k', str(chunk_audio)])
        cmd = [mlx, str(chunk_audio), '--model', args.model, '--language', args.language, '--output-format', 'json', '--output-dir', str(out_dir), '--output-name', chunk_audio.stem, '--verbose', 'False']
        if prompt:
            cmd.extend(['--initial-prompt', prompt])
        run(cmd)
        raw = json.loads((out_dir / f'{chunk_audio.stem}.json').read_text(encoding='utf-8'))
        kept = []
        for s in raw.get('segments', []):
            abs_start = float(s.get('start', 0)) + chunk_start
            abs_end = float(s.get('end', 0)) + chunk_start
            text = clean_text(s.get('text', '').strip())
            if suspicious(text):
                continue
            # trim overlap duplicates by keeping central region preference
            if idx > 0 and abs_start < start:
                continue
            if start + seg < duration and abs_start >= start + seg:
                continue
            kept.append({'start': abs_start, 'end': abs_end, 'text': text})
        merged_segments.extend(kept)
        chunks_meta.append({'index': idx, 'start': start, 'chunk_start': chunk_start, 'chunk_dur': chunk_dur, 'kept_segments': len(kept)})

    merged_segments.sort(key=lambda x: x['start'])
    # merge near-duplicate neighboring texts
    compact = []
    for s in merged_segments:
        if compact and s['text'] == compact[-1]['text'] and s['start'] - compact[-1]['end'] < 1.5:
            compact[-1]['end'] = s['end']
        else:
            compact.append(s)

    full_text = ' '.join(s['text'] for s in compact)
    full_text = clean_text(full_text)
    payload = {'language': args.language, 'segments': compact, 'text': full_text, 'chunks': chunks_meta}
    raw_json = out_dir / 'transcript.segmented.json'
    raw_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    clean_md = out_dir / 'transcript.segmented.clean.md'
    timeline_md = out_dir / 'transcript.segmented.timeline.md'
    txt = out_dir / 'transcript.segmented.txt'
    txt.write_text(full_text + '\n', encoding='utf-8')
    clean_md.write_text('# 分段转写清洁版\n\n## 全文\n\n' + full_text + '\n', encoding='utf-8')
    lines = ['# 分段转写时间线版', '']
    for s in compact:
        lines += [f"## {fmt_hms(s['start'])} - {fmt_hms(s['end'])}", '', s['text'], '']
    timeline_md.write_text('\n'.join(lines), encoding='utf-8')

    print(json.dumps({'status': 'ok', 'outputs': {'raw_json': str(raw_json), 'text': str(txt), 'clean_md': str(clean_md), 'timeline_md': str(timeline_md)}, 'chunks': chunks_meta[:5], 'segment_count': len(compact)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
