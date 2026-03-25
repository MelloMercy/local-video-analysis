#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
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


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def normalize_text(text: str) -> str:
    out = ' '.join((text or '').split())
    for a, b in TERM_FIXES:
        out = out.replace(a, b)
    return out


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


def fmt_ts(sec):
    x = int(float(sec))
    h = x // 3600
    m = (x % 3600) // 60
    s = x % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def summarize_text(text: str, limit=280):
    text = normalize_text(text)
    if len(text) <= limit:
        return text or '待补充'
    return text[:limit].rstrip() + '…'


def build_timeline(segments, bucket_seconds=60):
    buckets = defaultdict(list)
    for seg in segments:
        start = int(float(seg.get('start', 0)))
        bucket = start // bucket_seconds
        t = normalize_text(seg.get('text') or '')
        if t:
            buckets[bucket].append(t)
    out = []
    for bucket in sorted(buckets.keys()):
        start = bucket * bucket_seconds
        end = start + bucket_seconds
        merged = ' '.join(buckets[bucket])
        out.append((fmt_ts(start), fmt_ts(end), summarize_text(merged, 220)))
    return out


def sentence_split(text: str):
    text = normalize_text(text)
    return [x.strip() for x in re.split(r'(?<=[。！？.!?])\s+', text) if x.strip()]


def bullet_points_from_text(summary: str, timeline, max_points=6):
    points = []
    for s in sentence_split(summary):
        if len(s) < 18:
            continue
        points.append(summarize_text(s, 110))
        if len(points) >= max_points:
            return points
    for _, _, line in timeline:
        if len(line) < 18:
            continue
        points.append(summarize_text(line, 110))
        if len(points) >= max_points:
            break
    seen = []
    uniq = []
    for p in points:
        if p not in seen:
            seen.append(p)
            uniq.append(p)
    return uniq[:max_points]


def extract_probe_fields(probe: dict):
    duration = (
        probe.get('duration_seconds')
        or probe.get('duration')
        or probe.get('format', {}).get('duration')
        or probe.get('video', {}).get('duration')
    )
    width = (
        probe.get('width')
        or probe.get('pixel_width')
        or probe.get('video', {}).get('width')
    )
    height = (
        probe.get('height')
        or probe.get('pixel_height')
        or probe.get('video', {}).get('height')
    )
    return duration, width, height


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-dir', required=True)
    p.add_argument('--output', default='report.final.md')
    args = p.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    source = load_json(run_dir / 'source_result.json')
    probe = load_json(run_dir / 'probe.json')
    precise = load_json(run_dir / 'precise' / 'precise_transcript.json')
    base_transcript = load_json(run_dir / 'transcript.json')

    transcript = precise if precise.get('text') else base_transcript
    text = normalize_text(transcript.get('text', ''))
    segments = transcript.get('segments', [])

    duration, width, height = extract_probe_fields(probe)
    resolution = f'{width} x {height}' if width and height else 'unknown'

    overview = [
        f"- 输入来源：`{source.get('kind', 'unknown')}`",
        f"- 原始输入：`{source.get('source', 'unknown')}`",
        f"- 解析视频路径：`{source.get('video_path', 'unknown')}`",
        f"- 来源平台：`{source.get('source_host', 'unknown')}`",
        f"- 来源标题：`{source.get('source_title', 'unknown')}`",
        f"- 来源 ID：`{source.get('source_id', 'unknown')}`",
        f"- Run 名：`{source.get('suggested_run_name', run_dir.name)}`",
        f"- 分析目录：`{run_dir}`",
        f"- 时长：`{human_duration(duration)}`",
        f"- 分辨率：`{resolution}`",
    ]

    timeline = build_timeline(segments)
    summary = summarize_text(text, 800)
    points = bullet_points_from_text(summary, timeline)

    parts = ['# 视频分析报告', '', '## 视频概览', '', *overview, '', '## 整段总结', '', summary or '待补充', '', '## 时间线', '']
    if timeline:
        for start, end, line in timeline[:12]:
            parts += [f'### {start} - {end}', '', line, '']
    else:
        parts += ['- 待补充', '']

    parts += ['## 重点提取', '']
    if points:
        parts += [f'- {p}' for p in points]
    else:
        parts += ['- 待补充']
    parts += ['', '## 风险与问题', '', '- 自动生成结果，建议对关键术语和关键时间段做人工复核。', '- 若来源为平台 URL，则下载成功率受平台策略影响，属于 best-effort。', '', '## 可执行建议', '', '- 优先阅读 `precise/precise_transcript.clean.md` 与 `precise/precise_transcript.timeline.md`。', '- 若需更高可信度，复核 `precise/suspicious_segments.md`（若存在内容）。', '- 若需更完整最终稿，可结合关键帧做二次整理。', '', '## 方法局限', '', '- 当前报告由元信息、自动转写与自动拼装生成。', '- 该版本适合作为高质量草案，不应直接视为正式字幕级逐字稿。', '']

    out = run_dir / args.output
    out.write_text('\n'.join(parts), encoding='utf-8')
    print(str(out))


if __name__ == '__main__':
    main()
