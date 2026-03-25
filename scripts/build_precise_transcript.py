#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent

TERM_FIXES = [
    ('OpenCloud', 'OpenClaw'),
    ('Open Cloud', 'OpenClaw'),
    ('多Engine', '多 Agent'),
    ('Feishu通道', 'Feishu 通道'),
    ('APPSecret', 'App Secret'),
    ('APP ID', 'App ID'),
    ('全站工程师', '全栈工程师'),
    ('全站开发工程师', '全栈工程师'),
    ('project manager', 'project_manager'),
    ('Project Manager', 'project_manager'),
    ('sessionkey', 'sessionKey'),
    ('agenttoagent', 'agentToAgent'),
]


def suspicious(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    bad = ['卖卖卖卖', '我会变得更多的我会变得更多的', '����', '�']
    if any(x in t for x in bad):
        return True
    cur = mx = 1
    for i in range(1, len(t)):
        if t[i] == t[i - 1]:
            cur += 1
            mx = max(mx, cur)
        else:
            cur = 1
    return mx >= 8


def normalize(text: str) -> str:
    out = ' '.join(text.split())
    for a, b in TERM_FIXES:
        out = out.replace(a, b)
    return out


def fmt_ts(sec: float) -> str:
    x = int(sec)
    h = x // 3600
    m = (x % 3600) // 60
    s = x % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('audio_path')
    p.add_argument('--out-dir', required=True)
    p.add_argument('--prompt-file')
    p.add_argument('--model', default='mlx-community/whisper-large-v3-turbo')
    args = p.parse_args()

    root = Path(args.out_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    audio = Path(args.audio_path).expanduser().resolve()

    enhance = root / 'audio.enhanced.m4a'
    subprocess.run(['bash', str(SCRIPT_DIR / 'enhance_audio.sh'), str(audio), str(enhance)], check=True)

    base_dir = root / 'base'
    retry_dir = root / 'retry'
    base_dir.mkdir(exist_ok=True)
    retry_dir.mkdir(exist_ok=True)

    subprocess.run([
        'python3', str(SCRIPT_DIR / 'transcribe_audio.py'),
        str(enhance), '--model', args.model,
        '--prompt-file', args.prompt_file or '', '--prompt-mode', 'auto',
        '--output-dir', str(base_dir), '--output-name', 'transcript'
    ], check=True)

    raw = load_json(base_dir / 'transcript.json')
    segments = raw.get('segments', [])
    refined: List[Dict] = []
    suspicious_segments: List[Dict] = []

    ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'

    for idx, seg in enumerate(segments):
        text = normalize(seg.get('text', '').strip())
        start = float(seg.get('start', 0))
        end = float(seg.get('end', 0))
        item = {'start': start, 'end': end, 'text': text}
        if suspicious(text):
            suspicious_segments.append({'index': idx, **item})
            clip = retry_dir / f'sus_{idx:04d}.m4a'
            subprocess.run([
                ffmpeg, '-y', '-ss', str(max(0, start - 0.8)), '-to', str(end + 0.8),
                '-i', str(enhance), '-vn', '-c:a', 'aac', '-b:a', '128k', str(clip)
            ], check=True, capture_output=True, text=True)
            candidates = []
            retry_specs = [
                ('tiny_prompt', 'mlx-community/whisper-tiny', 'on'),
                ('turbo_auto', args.model, 'auto'),
            ]
            for tag, model, prompt_mode in retry_specs:
                outdir = retry_dir / f'{tag}_{idx:04d}'
                outdir.mkdir(exist_ok=True)
                subprocess.run([
                    'python3', str(SCRIPT_DIR / 'transcribe_audio.py'),
                    str(clip), '--model', model,
                    '--prompt-file', args.prompt_file or '', '--prompt-mode', prompt_mode,
                    '--output-dir', str(outdir), '--output-name', 'transcript'
                ], check=True)
                cand = load_json(outdir / 'transcript.json')
                cand_text = normalize(cand.get('text', '').strip())
                candidates.append({
                    'tag': tag,
                    'text': cand_text,
                    'suspicious': suspicious(cand_text),
                    'length': len(cand_text),
                })
            good = sorted(candidates, key=lambda c: (c['suspicious'], -c['length']))[0]
            item['text'] = good['text'] if good['text'] else text
            item['retry_selected'] = good['tag']
        refined.append(item)

    combined = ' '.join(x['text'] for x in refined if x['text'])
    marker = '我会变得更多的我会变得更多的'
    if marker in combined:
        combined = combined.split(marker)[0].rstrip('，,。 .')

    cleaned_segments = []
    acc = []
    for seg in refined:
        t = normalize(seg['text'])
        if not t:
            continue
        acc_text = (' '.join(acc + [t])).strip()
        if len(acc_text) <= len(combined) + 10:
            cleaned_segments.append({k: v for k, v in seg.items() if k != 'retry_selected' or v})
            acc.append(t)
        else:
            break

    out = {
        'text': combined,
        'segments': cleaned_segments,
        'suspicious_segments': suspicious_segments,
    }
    save_json(root / 'precise_transcript.json', out)
    (root / 'precise_transcript.txt').write_text(combined + '\n', encoding='utf-8')
    (root / 'precise_transcript.clean.md').write_text(
        '# 高精度逐字稿（实验版）\n\n## 全文\n\n' + combined + '\n', encoding='utf-8'
    )

    timeline = ['# 高精度逐字稿时间线（实验版）', '']
    for seg in cleaned_segments:
        timeline += [f"## {fmt_ts(seg['start'])} - {fmt_ts(seg['end'])}", '', seg['text'], '']
    (root / 'precise_transcript.timeline.md').write_text('\n'.join(timeline), encoding='utf-8')

    review = ['# 可疑片段清单', '']
    for seg in suspicious_segments:
        review += [f"- [{fmt_ts(seg['start'])} - {fmt_ts(seg['end'])}] {seg['text']}"]
    (root / 'suspicious_segments.md').write_text('\n'.join(review) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': 'ok',
        'outputs': {
            'json': str(root / 'precise_transcript.json'),
            'txt': str(root / 'precise_transcript.txt'),
            'clean_md': str(root / 'precise_transcript.clean.md'),
            'timeline_md': str(root / 'precise_transcript.timeline.md'),
            'review_md': str(root / 'suspicious_segments.md'),
        },
        'suspicious_count': len(suspicious_segments),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
