#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def slugify(text: str):
    safe = ''.join(c if c.isalnum() or c in '-_ .' else '-' for c in text)
    return '-'.join(safe.split()) or 'video-analysis'


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def read_text(path: Path):
    if not path.exists():
        return ''
    return path.read_text(encoding='utf-8')


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


def clean_markdown_for_summary(text: str):
    lines = []
    for raw in (text or '').splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('```'):
            continue
        if line in ('---', '***'):
            continue
        line = re.sub(r'^[-*+]\s+', '', line)
        line = re.sub(r'^\d+\.\s+', '', line)
        line = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', line)
        line = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', line)
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def extract_summary(run_dir: Path):
    final_report = run_dir / 'report.final.md'
    if final_report.exists():
        text = final_report.read_text(encoding='utf-8')
        marker = '## 整段总结'
        if marker in text:
            chunk = text.split(marker, 1)[1]
            chunk = chunk.split('## 时间线', 1)[0]
            cleaned = clean_markdown_for_summary(chunk)
            if cleaned:
                return summarize_text(cleaned, 260)
    clean_md = run_dir / 'precise' / 'precise_transcript.clean.md'
    if clean_md.exists():
        cleaned = clean_markdown_for_summary(clean_md.read_text(encoding='utf-8'))
        if cleaned:
            return summarize_text(cleaned, 260)
    transcript_clean = run_dir / 'transcript.clean.md'
    if transcript_clean.exists():
        cleaned = clean_markdown_for_summary(transcript_clean.read_text(encoding='utf-8'))
        if cleaned:
            return summarize_text(cleaned, 260)
    return '待补充'


def extract_key_points(run_dir: Path, limit=5):
    final_report = read_text(run_dir / 'report.final.md')
    if '## 重点提取' in final_report:
        chunk = final_report.split('## 重点提取', 1)[1]
        chunk = chunk.split('## 风险与问题', 1)[0]
        points = []
        for line in chunk.splitlines():
            line = line.strip()
            if line.startswith('- '):
                points.append(line)
            if len(points) >= limit:
                break
        if points:
            return points

    cleaned = clean_markdown_for_summary(read_text(run_dir / 'precise' / 'precise_transcript.clean.md'))
    if cleaned:
        sentences = re.split(r'(?<=[。！？.!?])\s+|\n+', cleaned)
        points = []
        for s in sentences:
            s = s.strip()
            if len(s) < 12:
                continue
            points.append(f'- {summarize_text(s, 100)}')
            if len(points) >= limit:
                break
        if points:
            return points
    return ['- 待补充']


def extract_timeline_preview(run_dir: Path, limit=3):
    final_report = read_text(run_dir / 'report.final.md')
    if '## 时间线' in final_report:
        chunk = final_report.split('## 时间线', 1)[1]
        chunk = chunk.split('## 重点提取', 1)[0]
        lines = []
        current = None
        for raw in chunk.splitlines():
            line = raw.strip()
            if line.startswith('### '):
                if current:
                    lines.append(current)
                current = {'title': line[4:].strip(), 'body': ''}
            elif line and current and not current['body']:
                current['body'] = summarize_text(line, 120)
        if current:
            lines.append(current)
        if lines:
            return lines[:limit]

    timeline_md = read_text(run_dir / 'precise' / 'precise_transcript.timeline.md')
    previews = []
    current_title = None
    for raw in timeline_md.splitlines():
        line = raw.strip()
        if line.startswith('## ') or line.startswith('### '):
            current_title = line.lstrip('#').strip()
        elif line and current_title:
            previews.append({'title': current_title, 'body': summarize_text(line, 120)})
            current_title = None
        if len(previews) >= limit:
            break
    return previews


def describe_frames(run_dir: Path):
    frames_dir = run_dir / 'frames'
    if not frames_dir.exists():
        return '- `frames/` not found in this export.', []
    image_files = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
        image_files.extend(sorted(frames_dir.glob(ext)))
    count = len(image_files)
    preview = [f.name for f in image_files[:6]]
    desc = f'- `frames/` contains `{count}` extracted frame files.'
    if preview:
        desc += f" Example files: `{', '.join(preview)}`"
    notes = [
        '- Use `frames/` when transcript wording is ambiguous or when UI / slide / on-screen state matters.',
        '- Prefer reviewing frames together with `precise_transcript.timeline.md` for higher confidence.',
    ]
    return desc, notes


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
    summary = extract_summary(run_dir)
    key_points = extract_key_points(run_dir)
    timeline_preview = extract_timeline_preview(run_dir)
    frames_desc, frame_notes = describe_frames(run_dir)

    key_points_md = '\n'.join(key_points)
    if timeline_preview:
        timeline_md = '\n\n'.join([f"### {x['title']}\n\n{x['body']}" for x in timeline_preview])
    else:
        timeline_md = '- 待补充'
    frame_notes_md = '\n'.join([frames_desc] + frame_notes)

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

## Recommended review path

1. Read `[[report.final]]` for the fastest overview.
2. Read `[[precise_transcript.clean]]` for transcript-first detail.
3. Read `[[precise_transcript.timeline]]` for chronological reconstruction.
4. Review `[[suspicious_segments]]` if confidence matters.
5. Cross-check with `frames/` when visual evidence matters.

## Summary

{summary}

## Key points

{key_points_md}

## Timeline preview

{timeline_md}

## Visual evidence

{frame_notes_md}

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


def render_entry_block(e):
    return [
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


def render_group_section(title, grouped):
    lines = [f'## {title}', '']
    if not grouped:
        return lines + ['- None yet.', '']
    for key in sorted(grouped.keys()):
        lines += [f'### {key}', '']
        for e in grouped[key]:
            lines += [f"- [[{e['entry_name']}/index|{e['title']}]] · `{e['date']}` · `{e['duration']}`"]
        lines += ['']
    return lines


def score_entry_for_pick(entry):
    score = 0
    summary = (entry.get('summary') or '').strip()
    if summary and summary != '待补充':
        score += 10
        score += min(len(summary), 200) / 50
    if entry.get('kind') == 'remote_url':
        score += 1
    if entry.get('duration') and entry.get('duration') != 'unknown':
        score += 1
    return score


def render_recommended_picks(entries, limit=5):
    lines = ['## Recommended picks', '']
    picks = sorted(entries, key=lambda e: (score_entry_for_pick(e), e.get('date', '')), reverse=True)
    picks = [e for e in picks if (e.get('summary') or '').strip() != '待补充'][:limit]
    if not picks:
        return lines + ['- No strong picks yet. Import more completed analyses first.', '']
    for e in picks:
        lines += [f"- [[{e['entry_name']}/index|{e['title']}]] · `{e['host']}` · `{e['date']}`", f"  - {e['summary']}"]
    lines += ['']
    return lines


def render_vault_index(entries):
    lines = ['# Local Video Analysis', '']
    lines += render_recommended_picks(entries)
    lines += ['## Recent analyses', '']
    if not entries:
        lines += ['- No analyses yet.', '']
    else:
        for e in entries:
            lines += render_entry_block(e)

    by_host = defaultdict(list)
    by_kind = defaultdict(list)
    for e in entries:
        by_host[e.get('host') or 'unknown'].append(e)
        by_kind[e.get('kind') or 'unknown'].append(e)

    lines += render_group_section('By source host', by_host)
    lines += render_group_section('By source kind', by_kind)
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
