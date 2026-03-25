#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def slugify(text: str):
    safe = ''.join(c if c.isalnum() or c in '-_ .' else '-' for c in text)
    return '-'.join(safe.split()) or 'video-analysis'


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def write_main_note(target_root: Path, run_dir: Path, source: dict, probe: dict):
    title = source.get('source_title') or source.get('suggested_run_name') or run_dir.name
    kind = source.get('kind', 'unknown')
    host = source.get('source_host', 'unknown')
    src = source.get('source', 'unknown')
    src_id = source.get('source_id', 'unknown')
    run_name = source.get('suggested_run_name', run_dir.name)
    duration = probe.get('duration_seconds') or probe.get('duration') or 'unknown'
    width = probe.get('width') or probe.get('pixel_width') or 'unknown'
    height = probe.get('height') or probe.get('pixel_height') or 'unknown'
    resolution = f'{width} x {height}' if width != 'unknown' and height != 'unknown' else 'unknown'
    today = datetime.now().strftime('%Y-%m-%d')

    note = f'''---
title: "{title}"
run_name: "{run_name}"
source_kind: "{kind}"
source_host: "{host}"
source_url: "{src}"
source_id: "{src_id}"
analysis_date: "{today}"
tags:
  - local-video-analysis
  - video-analysis
  - transcript
---

# {title}

## Overview

- Source kind: `{kind}`
- Source host: `{host}`
- Source URL: `{src}`
- Source ID: `{src_id}`
- Run name: `{run_name}`
- Duration: `{duration}`
- Resolution: `{resolution}`

## Entry points

- [[report.final]]
- [[report.stub]]
- [[transcript.clean]]
- [[transcript.timeline]]
- [[precise_transcript.clean]]
- [[precise_transcript.timeline]]
- [[suspicious_segments]]

## Notes

- `report.final.md` is the best default reading entry.
- `precise_transcript.clean.md` is the best transcript-first reading entry.
- `frames/` contains extracted visual evidence.
'''
    (target_root / 'index.md').write_text(note, encoding='utf-8')


def update_vault_index(vault_root: Path, subdir: str, entry_name: str, title: str, host: str, date_str: str):
    main_index = vault_root / subdir / 'index.md'
    main_index.parent.mkdir(parents=True, exist_ok=True)
    existing = main_index.read_text(encoding='utf-8') if main_index.exists() else '# Local Video Analysis\n\n## Recent analyses\n\n'
    line = f'- {date_str} · [[{entry_name}/index|{title}]] · `{host}`\n'
    if line not in existing:
        if '## Recent analyses\n\n' not in existing:
            existing = existing.rstrip() + '\n\n## Recent analyses\n\n'
        existing += line
    main_index.write_text(existing, encoding='utf-8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-dir', required=True)
    p.add_argument('--vault-dir', required=True)
    p.add_argument('--subdir', default='Local Video Analysis')
    args = p.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    vault_dir = Path(args.vault_dir).expanduser().resolve()
    entry_name = slugify(run_dir.name)
    target_root = vault_dir / args.subdir / entry_name
    target_root.mkdir(parents=True, exist_ok=True)

    source = load_json(run_dir / 'source_result.json')
    probe = load_json(run_dir / 'probe.json')

    wanted = [
        'report.final.md',
        'report.stub.md',
        'source_result.json',
        'probe.json',
        'transcript.clean.md',
        'transcript.timeline.md',
        'precise/precise_transcript.clean.md',
        'precise/precise_transcript.timeline.md',
        'precise/suspicious_segments.md',
    ]
    copied = []
    for rel in wanted:
        src = run_dir / rel
        if src.exists():
            dest = target_root / src.name
            shutil.copy2(src, dest)
            copied.append(str(dest))

    frames_dir = run_dir / 'frames'
    if frames_dir.exists():
        dest_frames = target_root / 'frames'
        if dest_frames.exists():
            shutil.rmtree(dest_frames)
        shutil.copytree(frames_dir, dest_frames)
        copied.append(str(dest_frames))

    write_main_note(target_root, run_dir, source, probe)
    copied.append(str(target_root / 'index.md'))

    title = source.get('source_title') or source.get('suggested_run_name') or run_dir.name
    host = source.get('source_host') or 'unknown'
    date_str = datetime.now().strftime('%Y-%m-%d')
    update_vault_index(vault_dir, args.subdir, entry_name, title, host, date_str)
    copied.append(str(vault_dir / args.subdir / 'index.md'))
    print('\n'.join(copied))


if __name__ == '__main__':
    main()
