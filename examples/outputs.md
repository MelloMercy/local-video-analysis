# Example Outputs

典型输出目录结构：

> 注：URL 输入时，`runs/` 下的目录名会优先基于视频标题 + 视频 ID 生成，而不是简单取 URL 路径最后一段。


```text
runs/<video-name>/
├── probe.json
├── frames/
├── audio.m4a
├── transcript.json
├── transcript.txt
├── transcript.clean.md
├── transcript.timeline.md
└── precise/
    ├── precise_transcript.json
    ├── precise_transcript.txt
    ├── precise_transcript.clean.md
    ├── precise_transcript.timeline.md
    └── suspicious_segments.md
```

## 文件说明

- `probe.json`：视频基础信息
- `frames/`：抽帧结果，用于画面分析
- `audio.m4a`：导出的音频
- `transcript.*`：基础转写与清洁版
- `precise_transcript.*`：高精度逐字稿实验版
- `suspicious_segments.md`：可疑片段人工复核入口

## 推荐阅读顺序

1. `precise_transcript.clean.md`
2. `precise_transcript.timeline.md`
3. `suspicious_segments.md`
4. 结合 `frames/` 做最终总结
