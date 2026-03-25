#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-dir', required=True)
    p.add_argument('--output', default='report.stub.md')
    args = p.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    source = load_json(run_dir / 'source_result.json')
    probe = load_json(run_dir / 'probe.json')

    duration = probe.get('duration_seconds') or probe.get('duration') or 'unknown'
    width = probe.get('width') or probe.get('pixel_width') or 'unknown'
    height = probe.get('height') or probe.get('pixel_height') or 'unknown'
    resolution = f'{width} x {height}' if width != 'unknown' and height != 'unknown' else 'unknown'

    content = f"""# 视频分析报告

## 视频概览

- 输入来源：`{source.get('kind', 'unknown')}`
- 原始输入：`{source.get('source', 'unknown')}`
- 解析视频路径：`{source.get('video_path', 'unknown')}`
- 来源平台：`{source.get('source_host', 'unknown')}`
- 来源标题：`{source.get('source_title', 'unknown')}`
- 来源 ID：`{source.get('source_id', 'unknown')}`
- Run 名：`{source.get('suggested_run_name', run_dir.name)}`
- 分析目录：`{run_dir}`
- 时长：`{duration}`
- 分辨率：`{resolution}`

## 整段总结

- 待补充：结合转写与画面生成整体总结。

## 时间线

- 待补充：按时间段组织关键内容。

## 重点提取

- 待补充：提取关键配置、命令、日志、交付物、风险点。

## 风险与问题

- 待补充：转写不确定性、平台下载限制、敏感信息风险等。

## 可执行建议

- 待补充：给出复现、扩展、继续分析建议。

## 方法局限

- 自动生成草案，建议结合人工复核。
- 平台 URL 下载为 best-effort。
"""
    out = run_dir / args.output
    out.write_text(content, encoding='utf-8')
    print(str(out))


if __name__ == '__main__':
    main()
