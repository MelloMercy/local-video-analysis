# Quick Start

## 1. 检查环境

```bash
python3 scripts/check_env.py
```

## 2. 跑完整流程（本地文件）

```bash
bash scripts/analyze_video.sh /path/to/video.mp4 30
```

## 3. 跑完整流程（视频 URL）

```bash
bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

## 3. 优先查看这些文件

- `runs/<video>/precise/precise_transcript.clean.md`
- `runs/<video>/precise/precise_transcript.timeline.md`
- `runs/<video>/precise/suspicious_segments.md`
- `runs/<video>/frames/`

## 4. 推荐工作流

先看高精度逐字稿，再结合抽帧做总结。

如果目标是正式逐字稿，请额外人工复核关键片段。
