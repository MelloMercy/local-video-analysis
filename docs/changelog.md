# Changelog

本文档记录这个项目已经完成、且对外沟通有价值的变化。

它不是逐条 git commit 镜像，而是更偏向：
- 用户能感知到什么变化
- 项目定位发生了什么变化
- 输出体验和使用路径有哪些重要升级

---

## 2026-03 — Homepage / docs / packaging refinement

这是一次围绕**项目表达、试用路径、对外包装**的集中整理。

### 1. GitHub 首页定位被重新拉直

README 首页不再只是“脚本说明”，而是更明确地表达成：

- 这不是普通视频摘要器
- 它是一条 **local-first / transcript-first** 的视频分析工作流
- 目标不是只给一个结论，而是产出一套**可复核、可继续加工、可沉淀进知识库**的材料包

这一轮重点补强了：
- 首屏定位语
- `At a glance`
- `Why this project`
- `Why it is not just another video summarizer`
- `Who this is for`

### 2. 新访客的试用路径更清楚了

README 和 quickstart 现在更强调：

- **先看真实样本**，而不是一上来先装环境
- 先判断输出风格是否适合自己
- 再决定要不要真的投入跑完整流程

新增 / 强化的关键入口包括：
- `Try this first`
- `docs/quickstart.md`
- README 里的 `Start here`

### 3. 真实验证样本被正式纳入说明体系

项目现在明确写出：

- 已经有真实公开视频样本完成过端到端验证
- 当前仓库保留了可直接查看的回归样本目录
- 用户可以直接打开真实输出判断质量，而不是只看概念描述

这让 README 从“纯介绍页”变成了“可立即验证的项目页”。

### 4. 运行环境要求前置到了 README

为了减少新访客进入仓库后的理解成本，README 现在直接写明：

- 当前主流程默认面向 **macOS 本地环境**
- 运行前至少需要：
  - Python 3.9+
  - `ffmpeg`
  - `ffprobe`
  - `swift`
  - `mlx-whisper`
- 最小检查命令：
  - `python3 scripts/check_env.py`

这样用户不用先跳进安装文档，才能知道门槛是什么。

### 5. Project / Skill 的关系被写清楚了

README 与 `docs/project-skill-sync.md` 现在更清楚地区分了两种使用方式：

- **As a project**
  - 用于开发、测试、版本管理、GitHub 协作
- **As an OpenClaw skill**
  - 用于在 OpenClaw 运行时里被直接调用

推荐心智模型现在明确为：

> project 负责长期建设，skill 负责稳定复用。

同时也补清了推荐部署顺序：

1. 先 clone 项目
2. 补依赖并通过环境检查
3. 先用 project 模式跑通真实样本
4. 确认输出符合预期
5. 再同步为 OpenClaw skill

### 6. GitHub 仓库外围包装同步升级

仓库外围信息也做了统一整理，包括：

- repo description
- topics

使其更贴近项目现在的真实定位，而不是只停留在“功能关键词列表”。

### 7. 新增对外传播文案包

新增：

- `docs/promo-copy.md`

这份文案包提供了：
- 中文一句话介绍
- 英文一句话介绍
- 短版介绍
- 中版介绍
- 极短版介绍
- 适合 / 不适合人群说明
- 对外表述时推荐固定带上的边界说明

这意味着项目现在不仅“能做”，而且已经具备了：
- 对外介绍
- 发群分享
- 发社群帖子
- 写简短宣传文案

所需的基础包装材料。

---

## Earlier notable changes

在这一轮包装整理之前，项目本身已经完成过一些关键升级：

### Obsidian 阅读链路升级

导出到 Obsidian 后，现在更像一套阅读空间，而不是工程文件堆：

- 每个 run 有自己的阅读入口
- 报告、逐字稿、时间线、可疑片段形成稳定阅读链路
- 仓库中已加入真实截图与流程图用于说明输出效果

### 真实 URL ingestion 验证

项目已经在真实 Bilibili 页面上完成过 best-effort URL ingestion 验证，证明这条输入路径不是纯理论设计。

### 术语修正与报告质量提升

逐字稿与最终报告相关脚本已经针对真实样本做过多轮修正，包括：
- 技术术语纠错
- 报告重点提取优化
- 输出元信息读取优化

---

## Recommended reading order for understanding the current state

如果你想理解项目现在已经发展到什么程度，建议按下面顺序看：

1. `README.md`
2. `docs/quickstart.md`
3. `docs/project-skill-sync.md`
4. `docs/promo-copy.md`
5. `docs/obsidian-integration.md`
6. `docs/url-inputs.md`

---

## Practical interpretation

截至这一轮，项目已经从“能跑的一套脚本”明显前进到：

- 有清晰定位
- 有真实样本
- 有明确试用路径
- 有 project / skill 双模式说明
- 有对外传播文案
- 有 GitHub 层面的完整包装

也就是说，它现在更像一个：

> **可继续迭代、可被理解、可被传播、可被复用的完整项目**
