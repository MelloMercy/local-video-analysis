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
- 对 **直链媒体文件**（如 `.mp4`）支持最稳定
- 对 **主流平台页面**采用 best-effort 策略
- 会尽量保存下载侧元信息（如 `source.info.json`）

## cookies / 登录态支持

可以通过环境变量把 cookies 支持接进主流程：

### 方式 1：使用 cookie 文件

```bash
LVA_COOKIE_FILE=/path/to/cookies.txt bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

### 方式 2：从浏览器读取 cookies

```bash
LVA_COOKIES_FROM_BROWSER=chrome bash scripts/analyze_video.sh "https://example.com/video-page" 30
```

当前支持的浏览器参数包括：
- `chrome`
- `safari`
- `firefox`
- `edge`
- `brave`
- `chromium`

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

## 出错时怎么理解

如果下载失败，优先判断：
- 是否需要 cookies / 登录态
- 是否是平台临时策略变化
- 是否是 DRM / 受限内容
- 是否可以换成直链 URL 或本地文件
