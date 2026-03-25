# Example Outputs

典型输出目录结构：

> 注：URL 输入时，`runs/` 下的目录名会优先基于视频标题 + 视频 ID 生成，而不是简单取 URL 路径最后一段。

```text
runs/<video-name>/
├── source_result.json
├── probe.json
├── report.stub.md
├── report.final.md
├── frames/
├── audio.m4a
├── transcript.clean.md
├── transcript.timeline.md
└── precise/
    ├── precise_transcript.clean.md
    ├── precise_transcript.timeline.md
    └── suspicious_segments.md
```

## 文件说明

- `source_result.json`：输入来源、解析方式、来源平台、来源标题、来源 ID
- `probe.json`：视频基础信息
- `report.stub.md`：报告草稿骨架
- `report.final.md`：结构化正式报告
- `frames/`：抽帧结果，用于画面分析
- `audio.m4a`：导出的音频
- `transcript.*`：基础转写与时间线
- `precise_transcript.*`：高精度逐字稿草案
- `suspicious_segments.md`：可疑片段人工复核入口

## 推荐阅读顺序

1. `report.final.md`
2. `precise/precise_transcript.clean.md`
3. `precise/precise_transcript.timeline.md`
4. `precise/suspicious_segments.md`
5. 结合 `frames/` 做最终复核

## 导出到 Obsidian 后

如果你把结果导出到 Obsidian，当前推荐从这里进入：

1. `Local Video Analysis/<run>/阅读首页.md`
2. `Local Video Analysis/<run>/01 视频分析报告.md`
3. `Local Video Analysis/<run>/02 高精度逐字稿.md`
4. `Local Video Analysis/<run>/03 时间线.md`
5. `Local Video Analysis/<run>/04 可疑片段.md`

## 这个输出结构适合什么

它更适合：
- 先快速看结论
- 再回到逐字稿查原话
- 再结合时间线和关键帧复核
- 最后沉淀成笔记、文档或报告
