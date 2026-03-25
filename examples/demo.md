# Demo

这个项目目前没有内置公开视频样本，主要原因是：
- 视频通常体积较大
- 很多真实样本涉及版权或隐私
- 不同视频类型会显著影响转写效果

但你可以用任意本地视频快速验证整个流程。

## 最小 demo

```bash
bash scripts/analyze_local_video.sh /path/to/video.mp4 30
```

跑完后优先看：

1. `runs/<video>/precise/precise_transcript.clean.md`
2. `runs/<video>/precise/precise_transcript.timeline.md`
3. `runs/<video>/precise/suspicious_segments.md`
4. `runs/<video>/frames/`

## 推荐测试视频类型

建议优先用这些视频测试：
- 单人中文技术讲解
- 教程录屏
- 配置演示
- 音乐较少、背景噪声较低的视频

不建议一开始就拿这些做首测：
- 多人同时说话
- 背景音乐很强
- 噪音很重
- 口音极强且语速极快

## 如何判断结果好不好

如果你看到：
- 主线完整
- 时间线可读
- 术语大体正确
- 尾部没有大段复读

那说明当前流程已经工作正常。

如果你要正式字幕级结果，请在当前输出基础上加一轮人工复核。
