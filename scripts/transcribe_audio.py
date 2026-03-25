#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_mlx_whisper():
    candidates = [
        shutil.which('mlx_whisper'),
        str(Path.home() / 'Library' / 'Python' / '3.9' / 'bin' / 'mlx_whisper'),
        str(Path.home() / '.local' / 'bin' / 'mlx_whisper'),
    ]
    return next((p for p in candidates if p and Path(p).exists()), None)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def load_prompt(prompt_path: Optional[Path]):
    if not prompt_path:
        return None
    if not prompt_path.exists():
        raise FileNotFoundError(f'prompt file not found: {prompt_path}')
    text = prompt_path.read_text(encoding='utf-8').strip()
    return text or None


def format_ts(seconds: float) -> str:
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f'{h:02d}:{m:02d}:{s:02d}'
    return f'{m:02d}:{s:02d}'


def clean_text(text: str) -> str:
    replacements = {
        'Open 可老': 'OpenClaw',
        'Open 可劳': 'OpenClaw',
        'Open可能': 'OpenClaw',
        'Obro': 'OpenClaw',
        '非书': 'Feishu',
        '輝殊': 'Feishu',
        'Fishu': 'Feishu',
        'A晶': 'agent',
        '艾进': 'agent',
        'Cescent Key': 'sessionKey',
        'Alorist': 'allowlist',
        'Alorphone': 'allowFrom',
        'Portject Manager': 'project_manager',
        '全戰工人是': 'full_stack_engineer',
        '全程工人士': 'full_stack_engineer',
        '主艾進': '主 agent',
        '小脈': '小麦',
        '小慢': '小栈',
        'APPC': 'App',
        '規程': 'Secret',
    }
    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)
    return ' '.join(out.split())


def write_outputs(raw_json_path: Path, payload: dict):
    text = payload.get('text', '').strip()
    segments = payload.get('segments', [])
    cleaned_full = clean_text(text)

    txt_path = raw_json_path.with_suffix('.txt')
    clean_md_path = raw_json_path.with_name(raw_json_path.stem + '.clean.md')
    timeline_md_path = raw_json_path.with_name(raw_json_path.stem + '.timeline.md')

    txt_path.write_text(cleaned_full + '\n', encoding='utf-8')

    clean_md = [
        '# 转写清洁版',
        '',
        f'- language: `{payload.get("language", "unknown")}`',
        f'- segments: `{len(segments)}`',
        '',
        '## 全文',
        '',
        cleaned_full,
        '',
    ]
    clean_md_path.write_text('\n'.join(clean_md), encoding='utf-8')

    timeline_lines = [
        '# 转写时间线版',
        '',
        f'- language: `{payload.get("language", "unknown")}`',
        f'- segments: `{len(segments)}`',
        '',
    ]
    for seg in segments:
        start = format_ts(float(seg.get('start', 0)))
        end = format_ts(float(seg.get('end', 0)))
        seg_text = clean_text(seg.get('text', '').strip())
        if not seg_text:
            continue
        timeline_lines.extend([
            f'## {start} - {end}',
            '',
            seg_text,
            '',
        ])
    timeline_md_path.write_text('\n'.join(timeline_lines), encoding='utf-8')

    return {
        'raw_json': str(raw_json_path),
        'text': str(txt_path),
        'clean_md': str(clean_md_path),
        'timeline_md': str(timeline_md_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('audio_path')
    parser.add_argument('--model', default='mlx-community/whisper-large-v3-turbo')
    parser.add_argument('--language', default='zh')
    parser.add_argument('--prompt-file')
    parser.add_argument('--prompt-mode', default='auto', choices=['auto', 'on', 'off'])
    parser.add_argument('--output-dir')
    parser.add_argument('--output-name')
    parser.add_argument('--verbose', default='False')
    args = parser.parse_args()

    audio = Path(args.audio_path).expanduser().resolve()
    if not audio.exists():
        print(f'file not found: {audio}', file=sys.stderr)
        sys.exit(2)

    mlx_whisper = find_mlx_whisper()
    if not mlx_whisper:
        print(json.dumps({
            'status': 'missing_dependency',
            'message': 'mlx_whisper not found. Install mlx-whisper first.'
        }, ensure_ascii=False, indent=2))
        sys.exit(3)

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else audio.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = args.output_name or audio.stem
    prompt_file = Path(args.prompt_file).expanduser().resolve() if args.prompt_file else None
    prompt = load_prompt(prompt_file) if prompt_file else None
    use_prompt = False
    if prompt:
        if args.prompt_mode == 'on':
            use_prompt = True
        elif args.prompt_mode == 'off':
            use_prompt = False
        else:
            use_prompt = 'large-v3-turbo' not in args.model

    cmd = [
        mlx_whisper,
        str(audio),
        '--model', args.model,
        '--language', args.language,
        '--output-format', 'json',
        '--output-dir', str(output_dir),
        '--output-name', output_name,
        '--verbose', args.verbose,
    ]
    if prompt and use_prompt:
        cmd.extend(['--initial-prompt', prompt])

    result = run(cmd)
    raw_json_path = output_dir / f'{output_name}.json'
    if not raw_json_path.exists():
        print(result.stdout.strip())
        print(result.stderr.strip(), file=sys.stderr)
        raise FileNotFoundError(f'expected transcript file not found: {raw_json_path}')

    payload = json.loads(raw_json_path.read_text(encoding='utf-8'))
    outputs = write_outputs(raw_json_path, payload)
    print(json.dumps({
        'status': 'ok',
        'model': args.model,
        'prompt_file': str(prompt_file) if prompt_file else None,
        'prompt_used': use_prompt,
        'outputs': outputs,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
