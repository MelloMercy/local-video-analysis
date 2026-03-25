#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

TERM_FIXES = [
    ('Cloud', 'Claude'),
    ('Cloud Code', 'Claude Code'),
    ('Cowork', 'CoWork'),
    ('computer use', 'Computer Use'),
    ('Computer use', 'Computer Use'),
    ('OPS4.6', 'Opus 4.6'),
    ('OPS 4.6', 'Opus 4.6'),
    ('国际相机', '国际象棋'),
    ('相机游戏', '象棋游戏'),
    ('麦克朗S', 'macOS'),
]

RUN_HOME = '阅读首页.md'
VAULT_HOME = '首页.md'
EXPORTED_FILES = {
    'report.final.md': '01 视频分析报告.md',
    'precise/precise_transcript.clean.md': '02 高精度逐字稿.md',
    'precise/precise_transcript.timeline.md': '03 时间线.md',
    'precise/suspicious_segments.md': '04 可疑片段.md',
    'report.stub.md': '附：报告草稿.md',
    'transcript.clean.md': '附：基础转写.md',
    'transcript.timeline.md': '附：基础时间线.md',
    'source_result.json': 'source_result.json',
    'probe.json': 'probe.json',
}


def slugify(text: str):
    safe = ''.join(c if c.isalnum() or c in '-_ .' else '-' for c in text)
    return '-'.join(safe.split()) or 'video-analysis'


def normalize_text(text: str):
    out = ' '.join((text or '').split())
    for a, b in TERM_FIXES:
        out = out.replace(a, b)
    return out


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def read_text(path: Path):
    if not path.exists():
        return ''
    return path.read_text(encoding='utf-8')


def summarize_text(text: str, limit=140):
    text = normalize_text(text)
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
        if line.startswith('#') or line.startswith('```') or line in ('---', '***'):
            continue
        line = re.sub(r'^[-*+]\s+', '', line)
        line = re.sub(r'^\d+\.\s+', '', line)
        line = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', line)
        line = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', line)
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def extract_probe_fields(probe: dict):
    duration = probe.get('duration_seconds') or probe.get('duration') or probe.get('format', {}).get('duration') or probe.get('video', {}).get('duration')
    width = probe.get('width') or probe.get('pixel_width') or probe.get('video', {}).get('width')
    height = probe.get('height') or probe.get('pixel_height') or probe.get('video', {}).get('height')
    if not (width and height):
        for stream in probe.get('streams', []):
            if stream.get('codec_type') == 'video':
                width = width or stream.get('width')
                height = height or stream.get('height')
                break
    return duration, width, height


def extract_section(text: str, start_marker: str, end_markers: list[str]):
    if start_marker not in text:
        return ''
    chunk = text.split(start_marker, 1)[1]
    for marker in end_markers:
        if marker in chunk:
            chunk = chunk.split(marker, 1)[0]
    return clean_markdown_for_summary(chunk).strip()


def extract_summary(run_dir: Path):
    final_report = run_dir / 'report.final.md'
    if final_report.exists():
        text = final_report.read_text(encoding='utf-8')
        overall = extract_section(text, '## 总体结论', ['## 核心观点'])
        scenarios = extract_section(text, '## 实战场景拆解', ['## 对比判断'])
        parts = []
        if overall:
            parts.append(overall)
        if scenarios:
            scenario_lines = []
            for line in scenarios.splitlines():
                line = re.sub(r'^\d+\.\s*', '', line).strip()
                if line:
                    scenario_lines.append(line)
                if len(scenario_lines) >= 3:
                    break
            if scenario_lines:
                parts.append('场景覆盖：' + '；'.join(scenario_lines) + '。')
        if parts:
            return '\n\n'.join(parts)
        brief = extract_section(text, '## 整段总结', ['## 总体结论', '## 时间线'])
        if brief:
            return brief
    return '待补充'


def extract_key_points(run_dir: Path, limit=4):
    final_report = read_text(run_dir / 'report.final.md')
    if '## 重点提取' in final_report:
        chunk = final_report.split('## 重点提取', 1)[1]
        chunk = chunk.split('## 风险与保留意见', 1)[0]
        points = []
        for line in chunk.splitlines():
            line = line.strip()
            if line.startswith('- '):
                points.append(normalize_text(line))
            if len(points) >= limit:
                break
        if points:
            return points
    return ['- 待补充']


def extract_timeline_preview(run_dir: Path, limit=3):
    final_report = read_text(run_dir / 'report.final.md')
    if '## 时间线' not in final_report:
        return []
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
            current['body'] = summarize_text(line, 80)
    if current:
        lines.append(current)
    return lines[:limit]


def describe_frames(run_dir: Path):
    frames_dir = run_dir / 'frames'
    if not frames_dir.exists():
        return '- 暂无 frames。', []
    image_files = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
        image_files.extend(sorted(frames_dir.glob(ext)))
    count = len(image_files)
    preview = [f.name for f in image_files[:4]]
    desc = f'- `frames/` 共 `{count}` 张。'
    if preview:
        desc += f" 例如：`{', '.join(preview)}`"
    notes = ['- 需要核对 UI、画面状态、操作步骤时，再结合 `03 时间线` 一起看。']
    return desc, notes


def write_run_home(target_root: Path, run_dir: Path, source: dict, probe: dict):
    title = source.get('source_title') or source.get('suggested_run_name') or run_dir.name
    kind = source.get('kind', 'unknown')
    host = source.get('source_host', 'unknown')
    src = source.get('source', 'unknown')
    src_id = source.get('source_id', 'unknown')
    run_name = source.get('suggested_run_name', run_dir.name)
    duration, width, height = extract_probe_fields(probe)
    resolution = f'{width} x {height}' if width and height else 'unknown'
    today = datetime.now().strftime('%Y-%m-%d')
    summary = extract_summary(run_dir)
    key_points = extract_key_points(run_dir)
    timeline_preview = extract_timeline_preview(run_dir)
    frames_desc, frame_notes = describe_frames(run_dir)

    key_points_md = '\n'.join(key_points)
    timeline_md = '\n\n'.join([f"### {x['title']}\n\n{x['body']}" for x in timeline_preview]) if timeline_preview else '- 待补充'
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

# 视频阅读首页

> {title}

## 一眼看完

- 来源：`{host}`
- 类型：`{kind}`
- 时长：`{human_duration(duration)}`
- 分辨率：`{resolution}`

## 先看哪里

1. [[01 视频分析报告]]
2. [[02 高精度逐字稿]]
3. [[03 时间线]]
4. [[04 可疑片段]]

## 快速摘要

{summary}

## 关键点

{key_points_md}

## 时间线预览

{timeline_md}

## 画面证据

{frame_notes_md}

## 附件

- [[附：报告草稿]]
- [[附：基础转写]]
- [[附：基础时间线]]
- `frames/`
'''
    (target_root / RUN_HOME).write_text(note, encoding='utf-8')


def load_index_entries(index_path: Path):
    data_path = index_path.with_suffix('.entries.json')
    if data_path.exists():
        try:
            return load_json(data_path) or []
        except Exception:
            return []
    return []


def render_entry_block(e):
    return [
        f"### [[{e['entry_name']}/{RUN_HOME[:-3]}|{e['title_short']}]]",
        '',
        f"- `{e['host']}` · `{e['duration']}` · `{e['date']}`",
        e['summary'],
        '',
    ]


def render_group_section(title, grouped):
    lines = [f'## {title}', '']
    if not grouped:
        return lines + ['- 暂无。', '']
    for key in sorted(grouped.keys()):
        lines += [f'### {key}', '']
        for e in grouped[key]:
            lines += [f"- [[{e['entry_name']}/{RUN_HOME[:-3]}|{e['title_short']}]] · `{e['date']}` · `{e['duration']}`"]
        lines += ['']
    return lines


def score_entry_for_pick(entry):
    score = 0
    summary = (entry.get('summary') or '').strip()
    if summary and summary != '待补充':
        score += 10
    if entry.get('duration') and entry.get('duration') != 'unknown':
        score += 1
    return score


def render_recommended_picks(entries, limit=3):
    lines = ['## 推荐先看', '']
    picks = sorted(entries, key=lambda e: (score_entry_for_pick(e), e.get('date', '')), reverse=True)
    picks = [e for e in picks if (e.get('summary') or '').strip() != '待补充'][:limit]
    if not picks:
        return lines + ['- 暂无。', '']
    for e in picks:
        lines += [f"- [[{e['entry_name']}/{RUN_HOME[:-3]}|{e['title_short']}]]", f"  - {e['summary']}"]
    lines += ['']
    return lines


def render_vault_home(entries):
    lines = ['# Local Video Analysis', '', '## 入口', '', '- 看新导入的视频：优先打开它的 `阅读首页`。', '- 想快速浏览历史结果：再看下面列表。', '']
    if len(entries) > 1:
        lines += render_recommended_picks(entries)
    lines += ['## 最近分析', '']
    if not entries:
        lines += ['- 暂无分析结果。', '']
    else:
        for e in entries:
            lines += render_entry_block(e)

    by_host = defaultdict(list)
    for e in entries:
        by_host[e.get('host') or 'unknown'].append(e)
    if len(by_host) > 1:
        lines += render_group_section('按来源网站看', by_host)
    return '\n'.join(lines) + '\n'


def update_vault_home(vault_root: Path, subdir: str, entry: dict):
    main_home = vault_root / subdir / VAULT_HOME
    main_home.parent.mkdir(parents=True, exist_ok=True)
    entries = load_index_entries(main_home)
    entries = [e for e in entries if e.get('entry_name') != entry['entry_name']]
    entries.insert(0, entry)
    entries.sort(key=lambda x: (x.get('date', ''), x.get('entry_name', '')), reverse=True)
    entries = entries[:100]
    main_home.write_text(render_vault_home(entries), encoding='utf-8')
    save_json(main_home.with_suffix('.entries.json'), entries)
    legacy_index = main_home.parent / 'index.md'
    if legacy_index.exists():
        legacy_index.unlink()


def clean_target_root(target_root: Path):
    if not target_root.exists():
        return
    keep = set(EXPORTED_FILES.values()) | {RUN_HOME, 'frames', '.obsidian'}
    for child in target_root.iterdir():
        if child.name not in keep:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()


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
    clean_target_root(target_root)

    source = load_json(run_dir / 'source_result.json')
    probe = load_json(run_dir / 'probe.json')
    duration, _, _ = extract_probe_fields(probe)

    copied = []
    for rel, exported_name in EXPORTED_FILES.items():
        src = run_dir / rel
        if src.exists():
            dest = target_root / exported_name
            shutil.copy2(src, dest)
            copied.append(str(dest))

    frames_dir = run_dir / 'frames'
    if frames_dir.exists():
        dest_frames = target_root / 'frames'
        if dest_frames.exists():
            shutil.rmtree(dest_frames)
        shutil.copytree(frames_dir, dest_frames)
        copied.append(str(dest_frames))

    write_run_home(target_root, run_dir, source, probe)
    copied.append(str(target_root / RUN_HOME))

    title = source.get('source_title') or source.get('suggested_run_name') or run_dir.name
    title_short = normalize_text(title)
    if len(title_short) > 28:
        title_short = title_short[:28].rstrip() + '…'
    entry = {
        'entry_name': entry_name,
        'title': title,
        'title_short': title_short,
        'host': source.get('source_host', 'unknown'),
        'kind': source.get('kind', 'unknown'),
        'duration': human_duration(duration),
        'run_name': source.get('suggested_run_name', run_dir.name),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'summary': extract_summary(run_dir),
    }
    update_vault_home(vault_dir, args.subdir, entry)
    copied.append(str(vault_dir / args.subdir / VAULT_HOME))
    copied.append(str((vault_dir / args.subdir / VAULT_HOME).with_suffix('.entries.json')))

    for path in copied:
        print(path)


if __name__ == '__main__':
    main()
