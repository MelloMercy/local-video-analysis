# Benchmark Landscape

这份对标报告用于帮助 `local-video-analysis` 明确：
- 同类项目都在做什么
- 我们和它们的相同点
- 我们真正的差异化在哪里
- 后续应该往哪条线继续加强

---

## 一、对标维度

本次对标按 3 类对象看：

1. **GitHub / Gitee 项目**
   - 侧重完整产品或脚本工作流
2. **Agent Skills / Skills Directory**
   - 侧重 skill 入口、能力命名、触发方式
3. **传统 Whisper + Summary 路线**
   - 侧重转写后直接总结的常见范式

---

## 二、GitHub / Gitee 项目

### 1. aschmelyun/subvert
- 类型：GitHub 项目
- 定位：从视频生成字幕、summary、chapters
- 借鉴价值：高

**和我们的相同点**
- 都处理视频
- 都覆盖转写后输出多种结果
- 都不只是单一字幕导出

**和我们的不同点**
- 它更偏成品化视频处理工具
- 我们更偏“逐字稿草案 + 抽帧 + 结构化总结底座”
- 我们更强调后续可复核、可增强

**值得借鉴的点**
- 项目包装方式
- 结果呈现方式
- 用户对“多输出形态”的理解路径

---

### 2. arashsajjadi/ai-powered-video-analyzer
- 类型：GitHub 项目
- 定位：offline 视频分析工具，含视觉识别、图像描述、Whisper 转写
- 借鉴价值：高

**和我们的相同点**
- 都强调本地 / offline
- 都把视频理解拆成多个步骤
- 都不是单纯 summary 脚本

**和我们的不同点**
- 它更偏多模态视觉分析
- 我们更偏 transcript-first
- 我们更强调教程 / 录屏 / 配置复盘

**值得借鉴的点**
- offline 定位表达
- 多模态能力叙事
- “视频分析器”而非“单脚本工具”的定位

---

### 3. Cell细胞/video2note
- 类型：Gitee 项目
- 定位：从视频提取音频、转写内容、生成结构化 Markdown 笔记
- 借鉴价值：高

**和我们的相同点**
- 都不是只停留在转写
- 都往 Markdown 结构化输出走
- 都适合技术学习 / 记录场景

**和我们的不同点**
- 它更偏“视频转技术笔记”
- 我们更偏“逐字稿底座 + 关键帧 + 联合总结”
- 我们现在更强调本地视频和 agent 工作流沉淀

**值得借鉴的点**
- Markdown 输出定位
- 技术学习场景表达
- “从视频到可读笔记”的叙事方式

---

### 4. mirabdullahyaser/Summarizing-Youtube-Videos-with-OpenAI-Whisper-and-GPT-3
- 类型：GitHub 项目
- 定位：YouTube 视频总结，Whisper + GPT
- 借鉴价值：中

**和我们的相同点**
- 都有 transcript → summary 链路
- 都依赖转写作为理解基础

**和我们的不同点**
- 它更像传统 baseline demo
- 它偏 YouTube / 云端总结
- 我们偏本地文件 / 本地流程 / 抽帧联动

**值得借鉴的点**
- 传统路线的 baseline 参照
- 帮助我们说明“我们为什么不是普通 Whisper + 总结项目”

---

### 5. SU-PER-NOVA/whisper-offline-video-audio-transcriber
- 类型：GitHub 项目
- 定位：离线视频/音频转文字工具
- 借鉴价值：中

**和我们的相同点**
- 都强调本地 / 离线
- 都覆盖视频转文字

**和我们的不同点**
- 它主要是转写工具
- 我们不只转写，还强调：
  - 抽帧
  - 后处理
  - 高精度逐字稿草案
  - 总结底座

**值得借鉴的点**
- 离线转写子能力的定位方式
- 如何对外表达“本地转写价值”

---

## 三、Skills 生态对标

### 1. liang121/video-summarizer
- 类型：skill
- 定位：视频总结
- 借鉴价值：高

**和我们的相同点**
- 都是视频 → 理解结果
- 都适合作为 agent 可直接触发能力

**和我们的不同点**
- 它更偏 summary 结果
- 我们更偏 transcript-first + frames + summary

**值得借鉴的点**
- skill 的命名直觉
- 用户入口的简洁性

---

### 2. liu-wei-ai/douyin-video-summary
- 类型：skill
- 定位：短视频总结
- 借鉴价值：高

**和我们的相同点**
- 都面向视频内容理解
- 都强调把视频转为可消费文本结果

**和我们的不同点**
- 它更偏内容消费 / 短视频总结
- 我们更偏教程、录屏、技术配置内容

**值得借鉴的点**
- 面向用户的能力包装
- 视频总结 skill 的需求验证

---

### 3. kar2phi/video-lens
- 类型：skill
- 定位：视频分析 / 视频理解
- 借鉴价值：高

**和我们的相同点**
- 都不是只做字幕
- 都强调“看懂视频”而不是只导出文本

**和我们的不同点**
- 它命名更产品化
- 我们更强调方法链路和 transcript 基础

**值得借鉴的点**
- 命名与定位的产品感
- “video understanding” 的外部表达方式

---

### 4. youtube-transcript-summarizer
- 类型：skill
- 定位：YouTube transcript → summary
- 借鉴价值：中高

**和我们的相同点**
- 都是 transcript-first
- 都以转写作为总结前提

**和我们的不同点**
- 它更偏线上平台内容
- 我们更偏本地文件 / 本地工作流

**值得借鉴的点**
- “先 transcript，再 summary” 的 skill 路线验证

---

## 四、我们真正的差异化

如果和这些项目 / skills 放在一起看，`local-video-analysis` 现在最值得强调的差异化是：

### 1. Local-first
不是先上传视频到云端，而是优先处理本地视频。

### 2. Transcript-first
不是只看几帧就总结，而是优先构建高质量自动逐字稿草案。

### 3. Frame + Transcript dual evidence
不是只靠音频，也不是只靠视觉，而是：
- 抽帧
- 转写
- 再做联合分析

### 4. Built for tutorial / recording workflows
比起泛视频总结，我们更适合：
- 技术教程
- 录屏
- 配置演示
- 开发过程复盘

### 5. Built for iteration
我们的结构天然支持后续继续增强：
- 术语白名单
- 可疑片段重跑
- 人工校对模式
- 多模型交叉转写

---

## 五、我们当前最像谁

如果只看相似度，我会这样判断：

### 最像的“项目侧”对象
1. `aschmelyun/subvert`
2. `arashsajjadi/ai-powered-video-analyzer`
3. `Cell细胞/video2note`

### 最像的“skill 侧”对象
1. `liang121/video-summarizer`
2. `liu-wei-ai/douyin-video-summary`
3. `kar2phi/video-lens`

---

## 六、我们的定位建议

结合这些对标对象，我建议我们继续坚持下面这条定位：

> **A local-first, transcript-first workflow for turning videos into precise transcript drafts, frame evidence, and structured summaries.**

中文可以表达为：

> **一个本地优先、逐字稿优先的视频分析工作流，用于把视频转成高质量转写草案、关键帧证据和结构化总结。**

这条定位比“video summarizer”更能体现我们的优势，也能和普通 Whisper+总结工具拉开差异。

---

## 七、建议下一步怎么用这些对标对象

### 如果目标是优化项目包装
优先参考：
- `aschmelyun/subvert`
- `Cell细胞/video2note`

### 如果目标是强化 offline / analyzer 定位
优先参考：
- `arashsajjadi/ai-powered-video-analyzer`

### 如果目标是优化 skill 入口
优先参考：
- `liang121/video-summarizer`
- `kar2phi/video-lens`

### 如果目标是强调我们的差异化
重点强调：
- local-first
- transcript-first
- tutorial / recording oriented
- frame + transcript merged analysis
- built for iterative precision improvement
