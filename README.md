# local-video-analysis

A local-first, transcript-first workflow for turning local videos or publicly accessible video URLs into precise transcript drafts, frame evidence, and structured summaries.

> Supports local video files and best-effort URL ingestion for publicly accessible video sources.

`local-video-analysis` 不是一个“吐一段摘要就结束”的视频工具。它的目标是把教程、录屏、技术讲解这类视频，整理成一套 **可复核、可继续加工、可沉淀进知识库** 的分析材料。

如果只用一句话概括它：

> 它更像一条把视频变成“可继续工作的材料包”的流程，而不是一个一次性视频摘要器。

## At a glance

- **Input**: local video file / public video URL
- **Core idea**: transcript first, then summary with frame evidence
- **Outputs**: transcript, timeline, frames, report, Obsidian reading entry
- **Best for**: tutorials, walkthroughs, screen recordings, technical explainers
- **Best used when**: you need evidence, traceability, and reusable notes — not just a quick summary

![Workflow overview](assets/flow-overview.svg)

## Why this project

很多视频分析流程的问题，不是“不能出摘要”，而是：

1. 太依赖云端服务
2. 只有结论，没有可追溯的逐字稿基础
3. 很难把视频内容沉淀成可复查、可继续加工的知识

换句话说，很多工具更擅长“快速给你一个结果”，但不擅长“给你一套还能继续工作的材料”。

这个项目的核心思路是：

> 先尽量把视频转成高质量逐字稿草案，再结合画面做结构化总结。

所以它更强调：
- local-first
- transcript-first
- frame + transcript dual evidence
- tutorial / recording oriented
- built for iterative precision improvement

## Why it is not just another video summarizer

它不是“看几帧然后输出一段总结”的轻量摘要器，而是更偏向一个**视频→材料包**的整理流程。

也就是说，它关心的不只是“最后一句结论”，还关心：
- 原话是否能回查
- 步骤是否能定位
- 画面是否有证据
- 输出是否还能继续沉淀进文档系统

所以它会把视频拆成多层可复核结果：

| Layer | What it preserves | Why it matters |
|---|---|---|
| Transcript | 原话基础 | 方便回查、纠错、提取术语 |
| Timeline | 时间结构 | 方便定位步骤、还原流程 |
| Frames | 画面证据 | 方便核对 UI、配置、操作状态 |
| Report | 结构化结论 | 方便快速理解视频主线 |
| Obsidian reading flow | 阅读入口 | 方便沉淀成长期可用知识 |

如果你的目标是：
- 复盘教程
- 提取配置步骤
- 回看录屏里的关键操作
- 把视频变成可继续整理的知识材料

这条路线会比“只要一段摘要”更有用。

## What it can do now

当前已经支持：
- 分析本地视频文件
- best-effort 分析公开可访问的视频 URL
- 统一产出转写、时间线、报告、关键帧和 Obsidian 阅读入口
- 为后续人工复核、知识沉淀、二次总结提供稳定底座

输入侧可以简单记成三类：
- **最稳**：本地视频文件
- **次稳**：直链媒体 URL
- **可尝试**：公开可访问的视频页面 URL

## Who this is for

这条工作流更适合你，如果你：

- 想把教程 / 录屏整理成**可回查资料**
- 想保留原话、时间线、关键画面
- 想把结果沉淀进 Obsidian、文档库或长期知识系统
- 接受先拿到高质量草案，再人工精修最后一段

如果你只是想快速看个大意，不关心过程证据，也不打算继续加工输出，那你大概率不需要它。

## Typical use cases

这个项目尤其适合：

- **教程视频复盘**：把长视频拆成逐字稿、时间线和重点结论
- **配置演示拆解**：保留每一步讲解和画面证据，方便回查
- **本地开发录屏归档**：把录屏沉淀成可以继续整理的资料
- **产品操作流程梳理**：既保留结果，也保留过程和证据
- **技术讲解内容整理**：方便后续写笔记、文档、报告或知识卡片

## Try this first

如果你是第一次看到这个仓库，最推荐先看真实样本，而不是先装环境。

当前仓库已经保留了一个真实跑通过的端到端样本：

```text
runs/claude新功能降维打击openclaw-桌面版cowork-code支持computer-use功能-6大实战场景全-bv1i6qbbcew2
```

建议先看：
- `report.final.md`
- `precise/precise_transcript.clean.md`
- `precise/precise_transcript.timeline.md`
- `precise/suspicious_segments.md`

这个样本已经验证过：
- 来源：公开可访问的 Bilibili 页面
- 运行方式：`bash scripts/analyze_video.sh '<url>' 30`
- 结论：在**不承诺全平台稳定**的前提下，best-effort URL ingestion 至少已在一个真实 Bilibili 页面上跑通

## Workflow at a glance

```text
video file / public URL
        ↓
source normalization
        ↓
audio + probe + frames
        ↓
transcript + precise transcript
        ↓
report.stub.md + report.final.md
        ↓
Obsidian 阅读首页 + 逐字稿 + 时间线 + 可疑片段
```

## What you get

运行一次分析后，通常会得到这些层次化结果：

```text
runs/<video-run>/
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

关键产物包括：
- `source_result.json`：输入来源与解析结果
- `probe.json`：时长、分辨率等视频元信息
- `frames/`：关键帧证据
- `audio.m4a`：导出的音频
- `transcript.clean.md` / `transcript.timeline.md`：基础转写与时间线
- `precise/precise_transcript.clean.md` / `precise/precise_transcript.timeline.md`：高精度逐字稿草案
- `precise/suspicious_segments.md`：可疑片段复核清单
- `report.stub.md` / `report.final.md`：结构化报告草稿与正式报告

## Reading experience after export

导出到 Obsidian 后，会变成更适合阅读的结构：

```text
<ObsidianVault>/
└── Local Video Analysis/
    └── <run-name>/
        ├── 阅读首页.md
        ├── 01 视频分析报告.md
        ├── 02 高精度逐字稿.md
        ├── 03 时间线.md
        ├── 04 可疑片段.md
        ├── source_result.json
        ├── probe.json
        └── frames/
```

### Real sample preview

![Obsidian export showcase](assets/obsidian-showcase.jpg)

![Obsidian reading flow](assets/obsidian-reading-flow.svg)

当前导出策略已经收敛成：
- 不再强调 vault 级首页
- 每条视频目录里的 `阅读首页.md` 是真正入口
- `阅读首页.md` 默认排在 `01 视频分析报告.md` 前面
- `01 视频分析报告.md`、`02 高精度逐字稿.md`、`03 时间线.md`、`04 可疑片段.md` 作为正式阅读链路

这让 Obsidian 更像阅读空间，而不是工程产物目录。

## Capability boundary

当前版本最适合：
- 教程视频
- 录屏视频
- 产品/工具演示
- 配置过程复盘
- 本地开发过程记录

当前版本已经比较稳定的是：
- 高质量自动逐字稿草案
- URL / 本地文件统一入口
- 结构化报告生成
- Obsidian 阅读导出

当前版本仍然保持保守预期：
- 更像“高质量自动草案”，不是正式发布级字幕
- 仍建议保留人工复核
- URL ingestion 是 best-effort，不宣称支持所有视频平台

如果你想快速判断它适不适合你的任务，可以用这三个问题筛一下：

1. 你是否更需要**可复核材料**，而不只是“一段摘要”？
2. 你的内容是否以**讲解 / 操作 / 演示 / 录屏**为主？
3. 你是否接受先得到**高质量草案**，再人工补最后一段精修？

如果这三个问题里有两个以上回答是“是”，这个项目通常就比较适合你。

## Runtime requirements

当前主流程默认面向 **macOS 本地环境**，运行前至少需要：

- Python 3.9+
- `ffmpeg`
- `ffprobe`
- `swift`
- `mlx-whisper`

最小检查命令：

```bash
python3 scripts/check_env.py
```

如果你还没装环境，先看：
- `docs/install.md`

## Start here

如果你第一次进仓库，建议按这个顺序看：

1. `Try this first` 这一节 — 先判断值不值得继续试
2. `docs/quickstart.md` — 看最快跑通路径
3. `docs/install.md` — 再补环境
4. `docs/workflow.md` — 理解完整处理链路
5. `docs/url-inputs.md` — 看 URL 输入边界
6. `docs/obsidian-integration.md` — 看导出后的阅读体验
7. `examples/outputs.md` — 看输出结构示例

## Quick start

主入口：
- `scripts/analyze_video.sh`

兼容入口：
- `scripts/analyze_local_video.sh`（wrapper，保留兼容，不再作为主推荐）

如果你只打算试一次，最推荐的顺序是：

1. 先用一个本地视频文件跑
2. 看 `report.final.md` 和 `precise/`
3. 觉得结果对味，再试 URL 输入和 Obsidian 导出

分析本地视频：

```bash
bash scripts/analyze_video.sh /path/to/video.mp4 30
```

分析公开视频 URL：

```bash
bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

需要浏览器 cookies 时：

```bash
LVA_COOKIES_FROM_BROWSER=chrome bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

导出到 Obsidian：

```bash
python3 scripts/export_to_obsidian.py --run-dir ./runs/<video-run> --vault-dir /path/to/your/ObsidianVault
```

## Docs map

- `docs/install.md` — 安装依赖与环境检查
- `docs/quickstart.md` — 最快跑通主流程
- `docs/workflow.md` — 完整处理链路说明
- `docs/url-inputs.md` — URL 输入、cookies 与失败边界
- `docs/obsidian-integration.md` — Obsidian 导出与阅读工作流
- `docs/report-template.md` — 报告头部元信息模板
- `docs/roadmap.md` — 后续能力规划
- `docs/project-skill-sync.md` — GitHub 项目与 OpenClaw skill 同步说明
- `docs/promo-copy.md` — 对外介绍 / 发群 / 发帖可复用文案
- `examples/outputs.md` — 输出结构示例

## Deployment / usage modes

这个能力建议按两种模式理解：

### 1. As a project

适合场景：
- 你要自己直接跑脚本
- 你要改代码、加能力、做 GitHub 协作
- 你要把它当作长期维护的主仓库

典型使用方式：

```bash
bash scripts/analyze_video.sh /path/to/video.mp4 30
python3 scripts/export_to_obsidian.py --run-dir ./runs/<video-run> --vault-dir /path/to/your/ObsidianVault
```

可以把它理解为：
- **Project = source of truth**
- 负责开发、测试、文档、版本演进

### 2. As an OpenClaw skill

适合场景：
- 你希望在 OpenClaw 里直接调用这套能力
- 你希望把它变成 agent 可以复用的工作流入口
- 你不想每次都手动记脚本和参数

可以把它理解为：
- **Skill = runtime entrypoint**
- 负责在 OpenClaw 里被直接使用

## Project + Skill

推荐双轨并存：

- **Project**：长期迭代、版本管理、GitHub 协作的 source of truth
- **Skill**：OpenClaw 直接调用入口

实践上就是：

> 先在 project 里迭代稳定能力，再同步回 skill。

## Recommended deployment flow

最推荐的部署 / 使用方式是：

1. 先把项目仓库 clone 到本地
2. 按 `docs/install.md` 补齐运行环境
3. 先用 **project 模式** 跑通一次
4. 确认输出风格、目录结构、Obsidian 导出都符合预期
5. 再把稳定能力同步成 **OpenClaw skill**

也就是说：

- **第一次接触**：优先 project
- **稳定复用**：再上 skill
- **后续迭代**：仍然以 project 为主，skill 跟随同步

## Roadmap

当前后续方向：
- terminology correction
- human review mode
- multi-model cross-checking
- batch processing
- subtitle-grade output quality
- 更稳的 URL ingestion 失败提示与降级建议

## License

MIT
