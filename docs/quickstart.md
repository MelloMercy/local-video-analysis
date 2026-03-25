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

## 5. 导出到 Obsidian

```bash
python3 scripts/export_to_obsidian.py --run-dir ./runs/<video-run> --vault-dir /path/to/your/ObsidianVault
```

导出后优先打开：

- `Local Video Analysis/index.md`（总览页）
- 或单条结果下的 `Local Video Analysis/<run>/index.md`

## 6. 优先查看这些文件

- `runs/<video>/precise/precise_transcript.clean.md`
- `runs/<video>/precise/precise_transcript.timeline.md`
- `runs/<video>/precise/suspicious_segments.md`
- `runs/<video>/frames/`

## 7. 推荐工作流

先看高精度逐字稿，再结合抽帧做总结。

如果目标是正式逐字稿，请额外人工复核关键片段。
