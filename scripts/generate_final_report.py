#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

TERM_FIXES = [
    ('Cloud', 'Claude'), ('Cloud Code', 'Claude Code'), ('Cowork', 'CoWork'),
    ('computer use', 'Computer Use'), ('Computer use', 'Computer Use'),
    ('OPS4.6', 'Opus 4.6'), ('OPS 4.6', 'Opus 4.6'), ('OpenCloud', 'OpenClaw'),
    ('opencloud', 'OpenClaw'), ('国际相机', '国际象棋'), ('相机游戏', '象棋游戏'),
    ('下相机', '下棋'), ('麦克朗S', 'macOS'), ('雅虎finance', '雅虎 Finance'),
    ('numbers', 'Numbers'), ('keynote', 'Keynote'), ('pages', 'Pages'), ('dispatch', 'Dispatch'),
]

SCENARIO_RULES = [
    ('视频封面', '整理桌面上的视频封面图片到单独文件夹，验证桌面文件识别与整理能力。'),
    ('Dispatch', '从手机端通过 Dispatch 给电脑发任务，验证跨设备下发与远程执行。'),
    ('博客', '调用浏览器打开博客、进入第二篇文章并总结内容，验证浏览器操作与阅读总结。'),
    ('Markdown', '把 Markdown 文件转换成 PDF，验证本地文档格式转换能力。'),
    ('雅虎 Finance', '从财经网站抓取特斯拉、苹果、微软、英伟达股价，验证联网检索与信息汇总。'),
    ('Numbers', '把股票数据写入 Numbers 表格并生成对比表，验证本地办公软件联动。'),
    ('Keynote', '基于抓取到的数据生成演示文稿，验证幻灯片制作能力。'),
    ('Pages', '继续生成 Pages 报告并改成中文，验证长文档生成与改写能力。'),
    ('国际象棋', '直接操控 macOS 桌面版国际象棋，验证非网页桌面应用与游戏场景操控。'),
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
    return f'{h}h {m}m {s}s' if h else f'{m}m {s}s'


def fmt_ts(sec):
    x = int(float(sec))
    h = x // 3600
    m = (x % 3600) // 60
    s = x % 60
    return f'{h:02d}:{m:02d}:{s:02d}'


def fmt_ts_short(sec):
    x = int(float(sec))
    h = x // 3600
    m = (x % 3600) // 60
    s = x % 60
    return f'{h:02d}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'


def summarize_text(text: str, limit=280):
    text = normalize_text(text)
    if len(text) <= limit:
        return text or '待补充'
    return text[:limit].rstrip() + '…'


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


def build_timeline(segments, bucket_seconds=60):
    buckets = defaultdict(list)
    for seg in segments:
        start = int(float(seg.get('start', 0)))
        bucket = start // bucket_seconds
        t = normalize_text(seg.get('text') or '')
        if t:
            buckets[bucket].append(t)
    out = []
    prev_summary = ''
    for bucket in sorted(buckets.keys()):
        start = bucket * bucket_seconds
        end = start + bucket_seconds
        merged = ' '.join(buckets[bucket])
        excerpt = summarize_text(merged, 180)
        summary = summarize_text((prev_summary + ' ' + merged).strip(), 90)
        out.append((fmt_ts(start), fmt_ts(end), summary, excerpt, merged))
        prev_summary = merged[-160:]
    return out


def build_key_points(text: str, timeline, title: str, max_points=8):
    points = []
    lowered_title = normalize_text(title).lower()
    rules = [
        ('桌面版', '视频围绕 Claude 桌面版能力展开演示。'),
        ('Computer Use', '核心展示点是 Computer Use / 桌面操控能力。'),
        ('CoWork', '视频展示了 CoWork / Code 入口的实际操作方式。'),
        ('手机', '视频专门演示了手机向电脑发任务并远程执行。'),
        ('博客', '视频验证了浏览器自动打开页面、进入文章并总结内容。'),
        ('Markdown', '视频验证了 Markdown 转 PDF 的本地文档处理能力。'),
        ('Numbers', '视频验证了写入 Numbers 表格的办公链路。'),
        ('Keynote', '视频验证了基于已有信息生成演示文稿。'),
        ('Pages', '视频验证了生成与改写报告文档。'),
        ('国际象棋', '视频重点展示了桌面版国际象棋操控，而不是网页场景。'),
        ('OpenClaw', '作者多次把 Claude 与 OpenClaw 做直接对比。'),
        ('开箱即用', '作者结论明显偏向强调 Claude 的开箱即用。'),
    ]
    text_pool = ' '.join([text] + [raw for _, _, _, _, raw in timeline])
    for needle, point in rules:
        if needle in text_pool or needle.lower() in lowered_title:
            points.append(point)
        if len(points) >= max_points:
            break
    return points[:max_points]


def detect_scenarios(title: str, timeline):
    text_pool = normalize_text(title + ' ' + ' '.join(raw for _, _, _, _, raw in timeline))
    scenarios = []
    for needle, desc in SCENARIO_RULES:
        if needle in text_pool:
            scenarios.append(desc)
    return scenarios


def build_overall_conclusion(title: str, scenarios, key_points):
    title_brief = re.sub(r'^[🚀✨🔥💥⭐️🌟]+', '', normalize_text(title)).strip(' ：:')
    scenario_count = len(scenarios)
    first = key_points[0].rstrip('。') if key_points else '视频围绕实际桌面操作展开'
    second = key_points[1].rstrip('。') if len(key_points) > 1 else '并通过多个连续案例证明流程可跑通'
    lines = []
    if title_brief and title_brief != 'unknown':
        lines.append(f'这段视频主要围绕《{title_brief}》展开。')
    lines.append(f'总体看，它不是单点演示，而是用 {scenario_count or "多个"} 个连续场景来证明：{first}；{second}。')
    return ' '.join(lines)


def build_core_view(text: str):
    t = normalize_text(text)
    views = []
    if '手机' in t and ('Dispatch' in t or '发送任务到电脑' in t):
        views.append('作者把“手机向电脑派发任务”作为区别于传统本地桌面操控的重要卖点。')
    if '国际象棋' in t:
        views.append('作者认为真正有说服力的部分，是能直接操控桌面版国际象棋这类非网页应用。')
    if 'OpenClaw' in t and '降维打击' in t:
        views.append('视频的表达立场非常鲜明：作者倾向认为 Claude 当前体验对 OpenClaw 构成明显优势。')
    if '开箱即用' in t or '不需要做任何配置' in t:
        views.append('作者反复强化“开箱即用、配置成本低”这一结论。')
    return views or ['待补充']


def build_comparison_judgment(text: str):
    t = normalize_text(text)
    lines = []
    if 'OpenClaw' in t:
        lines.append('视频中明确把 Claude 与 OpenClaw 做了直接对比，而且结论明显偏向 Claude。')
    if '降维打击' in t:
        lines.append('作者使用了“降维打击”这类强判断词，说明这不是中性测评，而是带明显主观倾向的体验表达。')
    if '开箱即用' in t or '不需要做任何配置' in t:
        lines.append('支撑这种判断的核心理由，是作者认为 Claude 更接近开箱即用，而 OpenClaw 需要更多配置与调试。')
    return lines or ['- 待补充']


def build_reservations(text: str):
    t = normalize_text(text)
    lines = [
        '这份报告基于自动转写与自动拼装生成，不等于人工完整复盘。',
        '视频里包含作者个人判断，尤其是对 Claude 与 OpenClaw 的对比，不能直接视为严格 benchmark 结论。',
        '桌面应用操控、办公软件联动、游戏场景这些演示说明“样例可行”，但不自动等于所有设备、权限、页面都稳定复现。',
    ]
    if '点赞' in t or '谢谢大家观看' in t:
        lines.append('视频后段包含明显自媒体收尾话术，自动摘要时应避免把这些内容误当成核心信息。')
    return lines


def build_summary(title: str, scenarios, key_points, core_views):
    title_brief = re.sub(r'^[🚀✨🔥💥⭐️🌟]+', '', normalize_text(title)).strip(' ：:')
    parts = []
    if title_brief and title_brief != 'unknown':
        parts.append(f'这段视频主要围绕《{title_brief}》展开。')
    if scenarios:
        parts.append(f'视频覆盖了 {len(scenarios)} 个连续实战场景，重点不是单一命令，而是完整演示 Claude 桌面版在文件整理、跨设备派发任务、浏览器操作、文档处理、办公软件联动和桌面游戏操控上的连续执行能力。')
    if core_views and core_views[0] != '待补充':
        parts.append(core_views[0])
    return ' '.join(parts)


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
    title = source.get('source_title', 'unknown')
    timeline = build_timeline(segments)
    key_points = build_key_points(text, timeline, title)
    scenarios = detect_scenarios(title, timeline)
    overall = build_overall_conclusion(title, scenarios, key_points)
    core_views = build_core_view(text)
    comparison = build_comparison_judgment(text)
    reservations = build_reservations(text)
    summary = build_summary(title, scenarios, key_points, core_views)

    overview = [
        f"- 输入来源：`{source.get('kind', 'unknown')}`",
        f"- 原始输入：`{source.get('source', 'unknown')}`",
        f"- 解析视频路径：`{source.get('video_path', 'unknown')}`",
        f"- 来源平台：`{source.get('source_host', 'unknown')}`",
        f"- 来源标题：`{title}`",
        f"- 来源 ID：`{source.get('source_id', 'unknown')}`",
        f"- Run 名：`{source.get('suggested_run_name', run_dir.name)}`",
        f"- 分析目录：`{run_dir}`",
        f"- 时长：`{human_duration(duration)}`",
        f"- 分辨率：`{resolution}`",
    ]

    parts = ['# 视频分析报告', '', '## 视频概览', '', *overview, '', '## 整段总结', '', summary or '待补充', '', '## 总体结论', '', overall, '', '## 核心观点', '']
    parts += [f'- {x}' for x in core_views]
    parts += ['', '## 实战场景拆解', '']
    parts += [f'{idx}. {item}' for idx, item in enumerate(scenarios, 1)] if scenarios else ['- 待补充']
    parts += ['', '## 对比判断', '']
    parts += [f'- {x}' for x in comparison]
    parts += ['', '## 时间线', '']
    if timeline:
        for start, end, minute_summary, excerpt, _ in timeline[:12]:
            start_label = start[3:] if start.startswith('00:') else start
            end_label = end[3:] if end.startswith('00:') else end
            parts += [f'### {start_label} - {end_label}', '', f'- 摘要：{minute_summary}', f'- 原文摘录：{excerpt}', '']
    else:
        parts += ['- 待补充', '']
    parts += ['## 重点提取', '']
    parts += [f'- {p}' for p in key_points] if key_points else ['- 待补充']
    parts += ['', '## 风险与保留意见', '']
    parts += [f'- {x}' for x in reservations]
    parts += ['', '## 可执行建议', '', '- 先读 `总体结论`、`核心观点`、`实战场景拆解`，再决定要不要深入时间线。', '- 若要复核是否真覆盖了所有场景，优先结合 `03 时间线` 与 `frames/` 交叉查看。', '- 若要形成更正式的对外分析稿，建议在当前结构化草案上做人工复核与补充。', '', '## 方法局限', '', '- 当前报告由元信息、自动转写与规则化拼装生成。', '- 该版本适合作为更全面的分析草案，不应直接视为正式字幕级逐字稿或严格评测报告。', '']
    out = run_dir / args.output
    out.write_text('\n'.join(parts), encoding='utf-8')
    print(str(out))

if __name__ == '__main__':
    main()
