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
    ('OpenCloud', 'OpenClaw'),
    ('opencloud', 'OpenClaw'),
    ('国际相机', '国际象棋'),
    ('相机游戏', '象棋游戏'),
    ('麦克朗S', 'macOS'),
    ('雅虎finance', '雅虎 Finance'),
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


def sentence_split(text: str):
    text = normalize_text(text)
    return [x.strip() for x in re.split(r'(?<=[。！？.!?])\s+', text) if x.strip()]


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
    for bucket in sorted(buckets.keys()):
        start = bucket * bucket_seconds
        end = start + bucket_seconds
        merged = ' '.join(buckets[bucket])
        out.append((fmt_ts(start), fmt_ts(end), summarize_text(merged, 220)))
    return out


def build_key_points(text_pool: str, title: str, max_points=8):
    points = []
    lowered_title = normalize_text(title).lower()
    rules = [
        ('桌面版', '视频围绕 Claude 桌面版能力展开。'),
        ('Computer Use', '重点展示了 Computer Use / 桌面操控能力。'),
        ('CoWork', '视频覆盖了 CoWork / Code 侧的入口与使用方式。'),
        ('手机', '视频展示了从手机向电脑发送任务并远程执行。'),
        ('博客', '演示了浏览器自动打开博客、进入文章并做内容总结。'),
        ('Markdown', '演示了把 Markdown 文件转换为 PDF。'),
        ('股票', '演示了抓取股票信息并整理成表格。'),
        ('Numbers', '演示了调用 Numbers 生成对比表。'),
        ('Keynote', '演示了调用 Keynote 生成演示文稿。'),
        ('Pages', '演示了调用 Pages 生成报告文档。'),
        ('国际象棋', '演示了直接操控桌面版国际象棋游戏。'),
        ('OpenClaw', '作者多次将 Claude 与 OpenClaw 做直接对比。'),
        ('开箱即用', '作者强调 Claude 的开箱即用体验。'),
    ]
    for needle, point in rules:
        if needle in text_pool or needle.lower() in lowered_title:
            points.append(point)
        if len(points) >= max_points:
            break
    return points[:max_points]


def extract_scenarios(text_pool: str):
    scenarios = [
        {
            'name': '桌面文件整理',
            'needles': ['封面', '图片都放在一个文件夹', '桌面上关于视频封面的所有图片'],
            'summary': '整理桌面上的视频封面图片，并自动归档到文件夹中。',
        },
        {
            'name': '手机派发电脑任务',
            'needles': ['dispatch', '发送任务到电脑', '手机上这里我打开了Claude的app'],
            'summary': '在手机端派发任务，让电脑端 Claude 通过浏览器完成操作并返回结果。',
        },
        {
            'name': '博客打开与内容总结',
            'needles': ['打开我的博客', '进入第二篇文章', '总结文章内容'],
            'summary': '调用浏览器打开博客、进入指定文章，并输出文章摘要。',
        },
        {
            'name': 'Markdown 转 PDF',
            'needles': ['markdown文件', '转为pdf', 'PDF格式'],
            'summary': '把本地 Markdown 文件转换成 PDF 交付物。',
        },
        {
            'name': '股票信息抓取 + Numbers 表格',
            'needles': ['股票信息', 'Numbers', '雅虎 Finance', '对比表'],
            'summary': '抓取多家公司的股票数据，并写入 Numbers 生成对比表。',
        },
        {
            'name': 'Keynote / Pages 办公文档生成',
            'needles': ['Keynote', '演示文稿', 'Pages', '报告已经创建完成'],
            'summary': '基于前面抓取的信息继续生成 Keynote 演示稿和 Pages 报告文档。',
        },
        {
            'name': '桌面版国际象棋操控',
            'needles': ['国际象棋', '走动棋子', '桌面版的国际象棋游戏'],
            'summary': '直接操控 macOS 桌面版国际象棋游戏，而不是只操作网页元素。',
        },
    ]
    found = []
    for item in scenarios:
        if any(n in text_pool for n in item['needles']):
            found.append(item)
    return found


def build_overall_conclusion(title: str, scenarios, text_pool: str):
    title = normalize_text(title).strip(' ：:')
    lines = []
    if title and title != 'unknown':
        lines.append(f'这条视频的主旨是围绕《{title}》展示 Claude 桌面版在真实电脑环境中的执行能力。')
    if scenarios:
        lines.append(f'从当前转写结果看，视频至少覆盖了 {len(scenarios)} 组连续演示场景，而不是只做单一 demo。')
    if 'OpenClaw' in text_pool and ('降维打击' in text_pool or '开箱即用' in text_pool):
        lines.append('作者的核心结论偏向于：Claude 在开箱即用和桌面操作流畅度上，明显优于他所熟悉的 OpenClaw 使用体验。')
    return ' '.join(lines) or '待补充'


def build_core_judgement(text_pool: str):
    items = []
    if 'Computer Use' in text_pool:
        items.append('作者重点想证明的不是聊天能力，而是 Claude 的桌面级 Computer Use 能力。')
    if '手机' in text_pool and '发送任务到电脑' in text_pool:
        items.append('视频把“手机给电脑派任务”作为一个关键卖点，用来证明跨设备协同体验。')
    if 'OpenClaw' in text_pool:
        items.append('视频中对 OpenClaw 的提及主要承担对照组角色，用来衬托 Claude 更省配置、更丝滑。')
    if '国际象棋' in text_pool:
        items.append('桌面版国际象棋演示承担“不是网页 automation，而是真桌面操控”的证明作用。')
    return items or ['- 待补充']


def build_scenario_lines(scenarios):
    lines = []
    for idx, item in enumerate(scenarios, 1):
        lines.append(f'{idx}. **{item["name"]}**：{item["summary"]}')
    return lines or ['- 待补充']


def build_comparison_judgement(text_pool: str):
    items = []
    if 'OpenClaw' in text_pool and '降维打击' in text_pool:
        items.append('作者给出的对比判断非常鲜明：他认为 Claude 对 OpenClaw 是“降维打击”。')
    if '开箱即用' in text_pool or '不需要做任何配置' in text_pool:
        items.append('支撑这个判断的主要理由是：Claude 更接近开箱即用，而不是需要长时间调配置。')
    if '丝滑' in text_pool:
        items.append('视频不断强调“丝滑”“操作快”，说明作者把流畅度和执行观感看得很重。')
    return items or ['- 待补充']


def build_risks(text_pool: str):
    items = [
        '自动生成结果，关键术语、关键时间段和作者态度仍建议人工复核。',
        '若来源为平台 URL，则下载成功率受平台策略影响，属于 best-effort。',
        '当前总结主要基于自动转写与规则抽取，覆盖度比“压缩摘要”更高，但仍不等于人工完整看完视频后的专业评述。',
    ]
    if '降维打击' in text_pool or '完全替代' in text_pool:
        items.append('视频作者的结论带有明显主观立场，适合作为体验型样本，不应直接视作严格 benchmark。')
    return items


def build_action_suggestions(scenarios):
    items = [
        '优先阅读 `precise/precise_transcript.clean.md` 与 `precise/precise_transcript.timeline.md` 做逐段复核。',
        '若要继续提升总结质量，建议针对“场景拆解”而不是单段摘要继续优化。',
    ]
    if scenarios:
        items.append('可进一步把每个实战场景单独抽成结构化卡片，形成更稳定的知识沉淀。')
    return items


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

    timeline = build_timeline(segments)
    text_pool = ' '.join([text] + [line for _, _, line in timeline])
    key_points = build_key_points(text_pool, title)
    scenarios = extract_scenarios(text_pool)
    overall = build_overall_conclusion(title, scenarios, text_pool)
    core_judgement = build_core_judgement(text_pool)
    comparison = build_comparison_judgement(text_pool)
    risks = build_risks(text_pool)
    suggestions = build_action_suggestions(scenarios)

    parts = ['# 视频分析报告', '', '## 视频概览', '', *overview, '']
    parts += ['## 总体结论', '', overall, '']
    parts += ['## 核心观点', '']
    parts += [f'- {x}' for x in core_judgement]
    parts += ['', '## 实战场景拆解', '']
    parts += build_scenario_lines(scenarios)
    parts += ['', '## 对比判断', '']
    parts += [f'- {x}' for x in comparison]
    parts += ['', '## 整段总结', '', summarize_text(overall + ' ' + ' '.join(key_points), 420), '']
    parts += ['## 时间线', '']
    if timeline:
        for start, end, line in timeline[:12]:
            parts += [f'### {start} - {end}', '', line, '']
    else:
        parts += ['- 待补充', '']
    parts += ['## 重点提取', '']
    parts += [f'- {p}' for p in key_points] if key_points else ['- 待补充']
    parts += ['', '## 风险与问题', '']
    parts += [f'- {x}' for x in risks]
    parts += ['', '## 可执行建议', '']
    parts += [f'- {x}' for x in suggestions]
    parts += ['', '## 方法局限', '', '- 当前报告由元信息、自动转写与规则抽取拼装生成。', '- 该版本已经比简单摘要更强调覆盖度，但仍不应直接视为正式字幕级逐字稿或人工精读结论。', '']

    out = run_dir / args.output
    out.write_text('\n'.join(parts), encoding='utf-8')
    print(str(out))


if __name__ == '__main__':
    main()
