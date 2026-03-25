# Install

## Required

- Python 3.9+
- ffmpeg
- ffprobe
- swift
- mlx-whisper

## macOS example

```bash
brew install ffmpeg
python3 -m pip install --user mlx-whisper
```

## Verify environment

```bash
python3 scripts/check_env.py
```

如果有依赖缺失，先补齐再运行主流程。
