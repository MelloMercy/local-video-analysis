# Obsidian Integration

`local-video-analysis` 现在不仅能生成转写、时间线和报告，还可以把结果整理成更适合 Obsidian 消费的阅读结构。

## 目标

把一次视频分析结果整理成：
- 一个单条视频的阅读入口页
- 一组可继续深挖的正式结果文件
- 一层可复核的底层证据

这样你在 Obsidian 里可以先读，再深入，而不是一上来面对一堆工程产物。

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

## 导出后的结构

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

## 阅读入口：`Local Video Analysis/<run>/阅读首页.md`

这个页面现在是单条分析结果的真正入口。

当前会包含：
- 一眼看完
- 先看哪里
- 完整摘要
- 关键点
- 时间线预览
- 画面证据

适合用来：
- 快速理解这条视频在讲什么
- 决定是否要继续看完整报告
- 决定是否要进一步看逐字稿、时间线和关键帧

## 正式阅读链路

当前推荐顺序：

1. `阅读首页.md`
2. `01 视频分析报告.md`
3. `02 高精度逐字稿.md`
4. `03 时间线.md`
5. `04 可疑片段.md`

## Frames 在这里的作用

`frames/` 不是装饰，它是视觉证据层。

适合这些场景：
- 转写里有模糊词、代词、省略句
- 屏幕录制里 UI / 配置 / 报错信息很重要
- 想确认某一步到底发生在什么画面状态下
- 想把逐字稿和真实屏幕内容交叉验证

最推荐的组合是：
- `03 时间线.md`
- `frames/`

一起看。

## 当前边界

当前 Obsidian 集成主要解决的是：
- 更好地消费分析结果
- 更方便地沉淀成知识
- 更自然地从“单次分析”走向“可复用阅读材料”

它当前不再强调：
- vault 级首页
- 总览型索引页
- 大而全的目录导航

现在更适合的定位是：

> 把单条视频分析结果导出成一个结构清晰、可直接阅读、适合继续整理的 Obsidian 阅读入口。
