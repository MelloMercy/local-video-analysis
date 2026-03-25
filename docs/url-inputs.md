# URL Inputs

项目现在支持两类输入源：

1. **本地视频文件**
2. **视频 URL**

## 设计原则

URL 输入层的目标不是做“万能下载器”，而是让视频分析工作流支持：
- 本地文件直接分析
- 可访问视频 URL 先拉取到本地，再进入统一处理流程

## 当前支持方式

- 通过 `yt-dlp` 处理视频 URL
- 对**直链媒体文件**（如 `.mp4`）支持最稳定
- 对**主流平台页面**采用 best-effort 策略

## 当前建议表述

建议在对外描述时写成：

> Supports local video files and best-effort URL ingestion for publicly accessible video sources.

而不要写成：

> Supports all video platforms.

## 已知现实约束

- 不同平台会频繁变更页面结构
- 某些平台需要 cookies / 登录态
- 某些内容可能存在 DRM / 访问限制
- 平台页下载成功率不应被过度承诺

## 最推荐的使用方式

- **最稳**：本地视频文件
- **次稳**：直链视频 URL
- **可尝试**：主流平台公开视频页（best-effort）
