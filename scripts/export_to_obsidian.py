#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

TERM_FIXES = [
    ('Cloud', 'Claude'), ('Cloud Code', 'Claude Code'), ('Cowork', 'CoWork'),
    ('computer use', 'Computer Use'), ('Computer use', 'Computer Use'),
    ('OPS4.6', 'Opus 4.6'), ('OPS 4.6', 'Opus 4.6'), ('国际相机', '国际象棋'),
    ('相机游戏', '象棋游戏'), ('麦克朗S', 'macOS'),
]
RUN_HOME = '阅读首页.md'
VAULT_HOME = '首页.md'
EXPORTED_FILES = {
    'report.final.md': '01 视频分析报告.md',
    'precise/precise_transcript.clean.md': '02 高精度逐字稿.md',
    'precise/precise_transcript.timeline.md': '03 时间线.md',
    'precise/suspicious_segments.md': '04 可疑片段.md',
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

def human_duration(seconds):
    try:
        x = int(float(seconds))
    except Exception:
        return 'unknown'
    h = x // 3600
    m = (x % 3600) // 60
    s = x % 60
    return f'{h}h {m}m {s}s' if h else f'{m}m {s}s'

def clean_markdown(text: str):
    lines = []
    for raw in (text or '').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or line.startswith('```') or line in ('---', '***'):
            continue
        line = re.sub(r'^[-*+]\s+', '', line)
        line = re.sub(r'^\d+\.\s+', '', line)
        line = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', line)
        line = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', line)
        line = line.strip()
        if line:
            lines.append(normalize_text(line))
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

def extract_section(text: str, start: str, ends: list[str]):
    if start not in text:
        return ''
    chunk = text.split(start, 1)[1]
    for marker in ends:
        if marker in chunk:
            chunk = chunk.split(marker, 1)[0]
    return clean_markdown(chunk)

def extract_summary(run_dir: Path):
    text = read_text(run_dir / 'report.final.md')
    if not text:
        return '待补充'
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
            parts.append('场景覆盖：\n- ' + '\n- '.join(scenario_lines))
    return '\n\n'.join(parts) if parts else '待补充'

def extract_key_points(run_dir: Path, limit=4):
    text = read_text(run_dir / 'report.final.md')
    if '## 重点提取' not in text:
        return ['- 待补充']
    chunk = text.split('## 重点提取', 1)[1].split('## 风险与保留意见', 1)[0]
    points = []
    for line in chunk.splitlines():
        line = line.strip()
        if line.startswith('- '):
            points.append(normalize_text(line))
        if len(points) >= limit:
            break
    return points or ['- 待补充']

def extract_timeline_preview(run_dir: Path, limit=3):
    text = read_text(run_dir / 'report.final.md')
    if '## 时间线' not in text:
        return []
    chunk = text.split('## 时间线', 1)[1].split('## 重点提取', 1)[0]
    blocks, current = [], None
    for raw in chunk.splitlines():
        line = raw.strip()
        if line.startswith('### '):
            if current:
                blocks.append(current)
            current = {'title': line[4:].strip(), 'summary': '', 'excerpt': ''}
        elif line.startswith('- 摘要：') and current:
            current['summary'] = line[5:].strip()
        elif line.startswith('- 原文摘录：') and current:
            current['excerpt'] = line[7:].strip()
    if current:
        blocks.append(current)
    return blocks[:limit]

def describe_frames(run_dir: Path):
    frames_dir = run_dir / 'frames'
    if not frames_dir.exists():
        return '- 暂无 frames。', []
    files = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
        files.extend(sorted(frames_dir.glob(ext)))
    preview = [f.name for f in files[:4]]
    desc = f'- `frames/` 共 `{len(files)}` 张。'
    if preview:
        desc += f" 例如：`{', '.join(preview)}`"
    return desc, ['- 需要核对 UI、画面状态、操作步骤时，再结合 `03 时间线` 一起看。']

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
    timeline_md = '\n\n'.join([f"### {x['title']}\n\n摘要：{x['summary']}\n\n原文摘录：{x['excerpt']}" for x in timeline_preview]) if timeline_preview else '- 待补充'
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

## 完整摘要
{summary}

## 关键点
{chr(10).join(key_points)}

## 时间线预览
{timeline_md}

## 画面证据
{frames_desc}
{chr(10).join(frame_notes)}
'''
    (target_root / RUN_HOME).write_text(note, encoding='utf-8')

def load_index_entries(index_path: Path):
    p = index_path.with_suffix('.entries.json')
    return load_json(p) if p.exists() else []

def render_entry_block(e):
    return [f"### [[{e['entry_name']}/{RUN_HOME[:-3]}|{e['title_short']}]]", '', f"- `{e['host']}` · `{e['duration']}` · `{e['date']}`", e['overall'], '', '#### 场景覆盖', *[f'- {x}' for x in e['scenarios']], '']

def render_group_section(title, grouped):
    lines = [f'## {title}', '']
    for key in sorted(grouped.keys()):
        lines += [f'### {key}', '']
        for e in grouped[key]:
            lines += [f"- [[{e['entry_name']}/{RUN_HOME[:-3]}|{e['title_short']}]] · `{e['date']}` · `{e['duration']}`"]
        lines += ['']
    return lines

def render_vault_home(entries):
    lines = ['# Local Video Analysis', '', '## 入口', '', '- 看新导入的视频：优先打开它的 `阅读首页`。', '- 想快速浏览历史结果：再看下面列表。', '', '## 最近分析', '']
    if not entries:
        lines += ['- 暂无分析结果。', '']
    else:
        for e in entries:
            lines += render_entry_block(e)
    by_host = {}
    for e in entries:
        by_host.setdefault(e.get('host') or 'unknown', []).append(e)
    if len(by_host) > 1:
        lines += render_group_section('按来源网站看', by_host)
    return '\n'.join(lines) + '\n'

def update_vault_home(vault_root: Path, subdir: str, entry: dict):
    main_home = vault_root / subdir / VAULT_HOME
    main_home.parent.mkdir(parents=True, exist_ok=True)
    entries = [e for e in load_index_entries(main_home) if e.get('entry_name') != entry['entry_name']]
    entries.insert(0, entry)
    entries.sort(key=lambda x: (x.get('date', ''), x.get('entry_name', '')), reverse=True)
    entries = entries[:100]
    main_home.write_text(render_vault_home(entries), encoding='utf-8')
    save_json(main_home.with_suffix('.entries.json'), entries)
    legacy_index = main_home.parent / 'index.md'
    if legacy_index.exists():
        legacy_index.unlink()

def clean_target_root(target_root: Path):
    keep = set(EXPORTED_FILES.values()) | {RUN_HOME, 'frames', '.obsidian'}
    for child in list(target_root.iterdir()) if target_root.exists() else []:
        if child.name not in keep:
            shutil.rmtree(child) if child.is_dir() else child.unlink()

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
    for rel, name in EXPORTED_FILES.items():
        src = run_dir / rel
        if src.exists():
            dest = target_root / name
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
    report = read_text(run_dir / 'report.final.md')
    overall = extract_section(report, '## 总体结论', ['## 核心观点']) or '待补充'
    scenarios_text = extract_section(report, '## 实战场景拆解', ['## 对比判断'])
    scenarios = []
    for line in scenarios_text.splitlines():
        line = re.sub(r'^\d+\.\s*', '', line).strip()
        if line:
            scenarios.append(line)
    title = source.get('source_title') or source.get('suggested_run_name') or run_dir.name
    title_short = normalize_text(title)
    if len(title_short) > 28:
        title_short = title_short[:28].rstrip() + '…'
    entry = {'entry_name': entry_name, 'title': title, 'title_short': title_short, 'host': source.get('source_host', 'unknown'), 'kind': source.get('kind', 'unknown'), 'duration': human_duration(duration), 'run_name': source.get('suggested_run_name', run_dir.name), 'date': datetime.now().strftime('%Y-%m-%d'), 'overall': overall, 'scenarios': scenarios[:4]}
    update_vault_home(vault_dir, args.subdir, entry)
    copied.append(str(vault_dir / args.subdir / VAULT_HOME))
    copied.append(str((vault_dir / args.subdir / VAULT_HOME).with_suffix('.entries.json')))
    for path in copied:
        print(path)

if __name__ == '__main__':
    main()
