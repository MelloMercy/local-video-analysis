# local-video-analysis

本地视频分析与逐字稿工作流。

这个项目用于把**本地视频**处理成一套可复用结果：
- 视频基础信息（probe）
- 抽帧结果
- 音频导出
- 基础转写
- 清洁版转写 / 时间线转写
- 高精度逐字稿（实验版）
- 可疑片段复核清单
- 后续用于生成总结 / 时间线 / 重点提取的原始材料

## 适合什么场景

特别适合：
- 教程视频
- 录屏视频
- 技术讲解
- 配置演示
- 本地开发过程录制

## 当前能力边界

当前版本已经达到：
- 高质量自动转写草案
- 适合教程类/录屏类视频的结构化总结前处理
- 高精度逐字稿实验版
- 可疑片段重跑
- 术语后处理与尾部幻觉清洗

当前版本还没有稳定达到：
- 可直接发布的正式字幕级逐字稿
- 全术语零误差
- 完全免人工复核

换句话说：

> 现在最适合的工作流是：**先拿高质量自动逐字稿，再结合视频画面做总结。**

---

## 项目结构

```text
local-video-analysis/
├── README.md
├── .gitignore
├── docs/
│   ├── install.md
│   ├── quickstart.md
│   ├── workflow.md
│   ├── roadmap.md
│   └── tech-glossary.txt
├── examples/
│   └── outputs.md
└── scripts/
    ├── analyze_local_video.sh
    ├── check_env.py
    ├── video_probe.py
    ├── extract_frames.swift
    ├── export_audio.swift
    ├── transcribe_audio.py
    ├── postprocess_transcript.py
    ├── enhance_audio.sh
    ├── build_precise_transcript.py
    └── transcribe_audio_segmented.py
```

---

## 安装依赖

先看：
- `docs/install.md`

最常见的 macOS 安装方式：

```bash
brew install ffmpeg
python3 -m pip install --user mlx-whisper
```

检查环境：

```bash
python3 scripts/check_env.py
```

---

## 快速开始

先看：
- `docs/quickstart.md`

完整流程：

```bash
bash scripts/analyze_local_video.sh /path/to/video.mp4 30
```

高精度逐字稿模式：

```bash
python3 scripts/build_precise_transcript.py /path/to/audio.m4a --out-dir ./runs/demo --prompt-file ./docs/tech-glossary.txt
```

---

## 典型输出

跑完后一般会得到：

- `probe.json`
- `frames/`
- `audio.m4a`
- `transcript.json`
- `transcript.clean.md`
- `transcript.timeline.md`
- `precise/precise_transcript.clean.md`
- `precise/precise_transcript.timeline.md`
- `precise/suspicious_segments.md`

更详细说明见：
- `examples/outputs.md`

---

## 推荐使用方式

推荐顺序：

1. 先跑 `analyze_local_video.sh`
2. 优先看 `precise_transcript.clean.md`
3. 再看 `precise_transcript.timeline.md`
4. 如果要更稳，人工复核 `suspicious_segments.md`
5. 最后结合抽帧结果做总结 / 时间线 / 重点提取

如果你的目标是：
- **教程复盘**
- **配置提取**
- **结构化总结**

那当前版本已经很好用。

如果你的目标是：
- **正式字幕级逐字稿**

那仍建议保留人工复核环节。

---

## License

MIT

---

## 项目与 skill 的关系

推荐做法：
- **项目** 负责长期演进、实验、版本管理、GitHub 托管
- **skill** 负责在 OpenClaw 内直接调用

也就是说：

> 先在项目里迭代，再同步到 skill。

---

## 未来升级方向

见：
- `docs/roadmap.md`

重点方向包括：
- 更强术语白名单
- 配置键名白名单纠错
- 关键片段人工校对模式
- 多模型交叉转写
- 更稳的字幕级逐字稿
