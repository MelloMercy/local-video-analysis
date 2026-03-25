# local-video-analysis

A local-first workflow for turning videos into structured, usable knowledge.

`local-video-analysis` 帮你把本地视频处理成一套更容易消费的结果：
- 视频基础信息（probe）
- 关键帧抽取
- 音频导出
- 基础转写
- 清洁版转写 / 时间线转写
- 高精度逐字稿（实验版）
- 可疑片段复核清单
- 供后续总结 / 时间线 / 重点提取使用的稳定输入材料

它特别适合：
- 教程视频
- 录屏视频
- 技术讲解
- 配置演示
- 本地开发过程录制

---

## Why this project

很多视频分析流程有两个常见问题：

1. **太依赖云端服务**
2. **只有摘要，没有可追溯的逐字稿基础**

这个项目的核心思路是：

> **先尽量把本地视频转成高质量自动逐字稿草案，再结合画面做总结。**

这样做的好处是：
- 更少遗漏
- 更容易追溯原话
- 更适合做教程复盘和配置提取
- 更适合后续继续增强精度

---

## What makes it useful

### 1. Local-first
默认面向本地视频、本地脚本、本地处理，不要求先上传整段视频。

### 2. Transcript-first
不是直接“看几帧就总结”，而是优先构建可复核的转写基础。

### 3. Structured outputs
输出不是一坨原始 JSON，而是分层结果：
- 基础转写
- 清洁版
- 时间线版
- 高精度逐字稿实验版
- 可疑片段清单

### 4. Built for iterative improvement
项目结构就是为后续升级准备的：
- 术语白名单增强
- 可疑片段重跑
- 人工校对模式
- 多模型交叉转写
- 更稳的字幕级输出

---

## Current capability boundary

当前版本已经达到：
- 高质量自动转写草案
- 适合教程类 / 录屏类视频的结构化总结前处理
- 高精度逐字稿实验版
- 可疑片段重跑
- 术语后处理与尾部幻觉清洗

当前版本还没有稳定达到：
- 可直接发布的正式字幕级逐字稿
- 全术语零误差
- 完全免人工复核

所以当前最推荐的使用方式是：

> **把它当作“高质量自动逐字稿 + 画面分析”的底座，而不是把它当成已经 100% 完成的字幕机。**

---

## Project structure

```text
local-video-analysis/
├── README.md
├── LICENSE
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

## Install

See:
- `docs/install.md`

Typical macOS setup:

```bash
brew install ffmpeg
python3 -m pip install --user mlx-whisper
```

Verify environment:

```bash
python3 scripts/check_env.py
```

---

## Quick start

See:
- `docs/quickstart.md`

Primary entrypoint:
- `scripts/analyze_video.sh`

Legacy compatibility entrypoint:
- `scripts/analyze_local_video.sh` (kept as a wrapper, but no longer the recommended primary command)

Run the full workflow with a local file:

```bash
bash scripts/analyze_video.sh /path/to/video.mp4 30
```

Run the full workflow with a video URL:

```bash
bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

If the platform page requires login:

```bash
LVA_COOKIES_FROM_BROWSER=chrome bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

Run the precise transcript pipeline only:

```bash
python3 scripts/build_precise_transcript.py /path/to/audio.m4a --out-dir ./runs/demo --prompt-file ./docs/tech-glossary.txt
```

---

## Typical outputs

Typical outputs include:

> For URL inputs, the run directory name is normalized from source metadata (title / video id) when available.


- `source_result.json`
- `probe.json`
- `report.stub.md`
- `frames/`
- `audio.m4a`
- `transcript.json`
- `transcript.clean.md`
- `transcript.timeline.md`
- `precise/precise_transcript.clean.md`
- `precise/precise_transcript.timeline.md`
- `precise/suspicious_segments.md`

See more in:
- `examples/outputs.md`

---

## Recommended workflow

1. Run `analyze_video.sh`
2. Read `precise_transcript.clean.md`
3. Read `precise_transcript.timeline.md`
4. Review `suspicious_segments.md` if you need more confidence
5. Use `report.stub.md` as the default report header scaffold
6. Combine transcript + frames for final summary / timeline / key points

If your goal is:
- tutorial review
- configuration extraction
- workflow reconstruction
- structured summaries

then the current version is already very useful.

If your goal is:
- release-grade subtitles

then keep a lightweight human review step.

---

## Project + Skill

Recommended split:
- **Project**: the source of truth for iteration, experiments, versioning, and GitHub collaboration
- **Skill**: the OpenClaw-facing entry point for direct agent use

In practice:

> iterate in the project first, then sync the stable workflow back into the skill.

---

## Roadmap

See:
- `docs/roadmap.md`

Main directions:
- stronger glossary and config-key correction
- better suspicious-segment detection
- lightweight human review mode
- multi-model cross-checking
- more stable subtitle-grade output

---

## Reporting recommendation

When generating a final report, include source metadata in the header whenever available:
- input kind (`local_file` / `remote_url`)
- original source
- resolved local video path
- source host
- source title
- source id
- run name

See:
- `docs/report-template.md`

---

## License

MIT
