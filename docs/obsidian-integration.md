# Obsidian Integration

`local-video-analysis` 现在不仅能生成转写、时间线和报告，还可以把结果整理成更适合 Obsidian 消费的知识库结构。

## 目标

把一次视频分析结果整理成：
- 一个 vault 级总览页
- 一个单条分析首页
- 一组可继续深挖的底层结果文件

这样你在 Obsidian 里可以先浏览，再深入，而不是直接面对一堆原始文件。

---

## 导出命令

```bash
python3 scripts/export_to_obsidian.py --run-dir ./runs/<video-run> --vault-dir /path/to/your/ObsidianVault
```

可选参数：

```bash
python3 scripts/export_to_obsidian.py \
  --run-dir ./runs/<video-run> \
  --vault-dir /path/to/your/ObsidianVault \
  --subdir "Local Video Analysis"
```

---

## 导出后的结构

```text
<ObsidianVault>/
└── Local Video Analysis/
    ├── index.md
    └── <run-name>/
        ├── index.md
        ├── report.final.md
        ├── report.stub.md
        ├── source_result.json
        ├── probe.json
        ├── transcript.clean.md
        ├── transcript.timeline.md
        ├── precise_transcript.clean.md
        ├── precise_transcript.timeline.md
        ├── suspicious_segments.md
        └── frames/
```

---

## Vault 首页：`Local Video Analysis/index.md`

这个页面是整个视频分析知识库的总入口。

当前会包含：
- Recommended picks
- Recent analyses
- By source host
- By source kind

适合用来：
- 快速找最近分析结果
- 优先读更完整的条目
- 按来源平台回看历史分析
- 区分 `local_file` / `remote_url` 两类输入

---

## 单条首页：`Local Video Analysis/<run>/index.md`

这个页面是单条分析结果的阅读首页。

当前会包含：
- Overview
- Recommended review path
- Summary
- Key points
- Timeline preview
- Visual evidence
- Entry points

适合用来：
- 快速理解这一条视频大致讲了什么
- 决定是否要进一步看逐字稿
- 决定是否需要结合帧做复核

---

## 推荐阅读顺序

### 想最快了解内容
1. `report.final.md`
2. 单条 `index.md` 里的 Summary / Key points / Timeline preview

### 想更稳地复核内容
1. `precise_transcript.clean.md`
2. `precise_transcript.timeline.md`
3. `suspicious_segments.md`
4. `frames/`

### 想做知识沉淀
1. 先从 vault 首页进入
2. 打开单条首页
3. 再深入到底层文件

---

## Frames 在这里的作用

`frames/` 不是装饰，它是视觉证据层。

适合这些场景：
- 转写里有模糊词、代词、省略句
- 屏幕录制里 UI / 配置 / 报错信息很重要
- 想确认某一步到底发生在什么画面状态下
- 想把逐字稿和真实屏幕内容交叉验证

最推荐的组合是：
- `precise_transcript.timeline.md`
- `frames/`

一起看。

---

## 当前边界

当前 Obsidian 集成主要解决的是：
- 更好地消费分析结果
- 更方便地沉淀成知识
- 更自然地从“单次分析”走向“可复用知识库”

它还没有做的是：
- 自动回写你的已有笔记体系
- 自动生成复杂双向链接网络
- 自动给现有 vault 做大规模重构

所以目前最适合的定位是：

> 把视频分析结果导出成一个结构清晰、可直接阅读、适合继续整理的 Obsidian 知识入口。
