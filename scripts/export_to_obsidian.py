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


def summarize_text(text: str, limit=140):
    text = ' '.join((text or '').split())
    if len(text) <= limit:
        return text or '待补充'
    return text[:limit].rstrip() + '…'


def human_duration(seconds):
    try:
        x = int(float(seconds))
    except Exception:
        return 'unknown'
    h = x // 3600
    m = (x % 3600) // 60
    s = x % 60
    if h:
        return f'{h}h {m}m {s}s'
    return f'{m}m {s}s'


def extract_summary(run_dir: Path):
    final_report = run_dir / 'report.final.md'
    if final_report.exists():
        text = final_report.read_text(encoding='utf-8')
        marker = '## 整段总结'
        if marker in text:
            chunk = text.split(marker, 1)[1]
            chunk = chunk.split('## 时间线', 1)[0]
            return summarize_text(chunk.strip())
    clean_md = run_dir / 'precise' / 'precise_transcript.clean.md'
    if clean_md.exists():
        return summarize_text(clean_md.read_text(encoding='utf-8'))
    return '待补充'


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
- Duration: `{human_duration(duration)}`
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


def load_index_entries(index_path: Path):
    if not index_path.exists():
        return []
    text = index_path.read_text(encoding='utf-8')
    marker = '<!-- INDEX_ENTRIES_START -->\n'
    if marker not in text:
        return []
    payload = text.split(marker, 1)[1].split('\n<!-- INDEX_ENTRIES_END -->', 1)[0].strip()
    if not payload:
        return []
    try:
        return json.loads(payload)
    except Exception:
        return []


def render_vault_index(entries):
    lines = ['# Local Video Analysis', '', '## Recent analyses', '']
    if not entries:
        lines += ['- No analyses yet.', '']
    else:
        for e in entries:
            lines += [
                f"### [[{e['entry_name']}/index|{e['title']}]]",
                '',
                f"- Date: `{e['date']}`",
                f"- Source host: `{e['host']}`",
                f"- Source kind: `{e['kind']}`",
                f"- Duration: `{e['duration']}`",
                f"- Run name: `{e['run_name']}`",
                '',
                e['summary'],
                '',
            ]
    lines += ['<!-- INDEX_ENTRIES_START -->', json.dumps(entries, ensure_ascii=False, indent=2), '<!-- INDEX_ENTRIES_END -->', '']
    return '\n'.join(lines)


def update_vault_index(vault_root: Path, subdir: str, entry: dict):
    main_index = vault_root / subdir / 'index.md'
    main_index.parent.mkdir(parents=True, exist_ok=True)
    entries = load_index_entries(main_index)
    entries = [e for e in entries if e.get('entry_name') != entry['entry_name']]
    entries.insert(0, entry)
    entries.sort(key=lambda x: (x.get('date', ''), x.get('entry_name', '')), reverse=True)
    entries = entries[:100]
    main_index.write_text(render_vault_index(entries), encoding='utf-8')


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
    entry = {
        'entry_name': entry_name,
        'title': title,
        'host': source.get('source_host') or 'unknown',
        'kind': source.get('kind') or 'unknown',
        'duration': human_duration(probe.get('duration_seconds') or probe.get('duration') or 'unknown'),
        'run_name': source.get('suggested_run_name', run_dir.name),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'summary': extract_summary(run_dir),
    }
    update_vault_index(vault_dir, args.subdir, entry)
    copied.append(str(vault_dir / args.subdir / 'index.md'))
    print('\n'.join(copied))


if __name__ == '__main__':
    main()
