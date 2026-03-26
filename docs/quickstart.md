# Quick Start

## 1. 检查环境

```bash
python3 scripts/check_env.py
```

## 2. 跑完整流程（本地文件）

主入口：

```bash
bash scripts/analyze_video.sh /path/to/video.mp4 30
```

兼容旧入口（仍可用，但不再推荐作为主入口）：

```bash
bash scripts/analyze_local_video.sh /path/to/video.mp4 30
```

## 3. 跑完整流程（视频 URL）

```bash
bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

## 4. 平台页需要登录态时

```bash
LVA_COOKIES_FROM_BROWSER=chrome bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

## 5. 用真实样本快速感受输出质量（推荐）

如果你刚进仓库，不想先自己准备视频，可以直接先看这个已验证样本：

```text
runs/claude新功能降维打击openclaw-桌面版cowork-code支持computer-use功能-6大实战场景全-bv1i6qbbcew2
```

建议先打开：

- `report.final.md`
- `precise/precise_transcript.clean.md`
- `precise/precise_transcript.timeline.md`
- `precise/suspicious_segments.md`

这样能最快判断：
- 这条工作流的报告风格你是否喜欢
- 逐字稿精度是否达到你的可用标准
- 你是否真的需要 Obsidian 导出链路

## 6. 导出到 Obsidian

```bash
python3 scripts/export_to_obsidian.py --run-dir ./runs/<video-run> --vault-dir /path/to/your/ObsidianVault
```

导出后优先打开：

- `Local Video Analysis/index.md`（总览页）
- 或单条结果下的 `Local Video Analysis/<run>/index.md`

更完整说明见：
- `docs/obsidian-integration.md`

## 7. 优先查看这些文件

- `runs/<video>/precise/precise_transcript.clean.md`
- `runs/<video>/precise/precise_transcript.timeline.md`
- `runs/<video>/precise/suspicious_segments.md`
- `runs/<video>/frames/`

## 8. 推荐工作流

先看高精度逐字稿，再结合抽帧做总结。

如果目标是正式逐字稿，请额外人工复核关键片段。

## 9. 什么时候应该优先换成本地文件

如果你用 URL 跑不通，不要先怀疑主流程本身，先优先判断是否属于输入侧问题：

- 页面需要登录态 / cookies
- 平台临时限制了抓取
- 页面不是公开视频
- 存在 DRM 或地区限制

这时最稳的降级路径通常是：

1. 先把视频拿到本地
2. 再用本地文件重新走 `analyze_video.sh`
3. 最后再决定要不要导出 Obsidian
