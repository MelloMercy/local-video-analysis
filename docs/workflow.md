# Workflow

## 标准流程

1. `video_probe.py`
   - 获取视频时长、分辨率、编码等基础信息

2. `extract_frames.swift`
   - 按时间间隔抽帧
   - 适合后续画面分析

3. `export_audio.swift`
   - 从视频导出音频

4. `transcribe_audio.py`
   - 生成基础转写
   - 支持 `large-v3-turbo`
   - `prompt-mode auto`：对 `large-v3-turbo` 默认不把术语表直接塞进 initial prompt

5. `postprocess_transcript.py`
   - 术语标准化
   - 尾部幻觉清洗

6. `build_precise_transcript.py`
   - 音频增强
   - 整段首轮转写
   - 可疑片段检测
   - 局部重跑
   - 合并高精度逐字稿实验版

7. 视觉 + 音频联合总结
   - 用关键帧补足画面信息
   - 用转写补足口播逻辑
   - 最终产出总结 / 时间线 / 重点提取

## 适合的视频类型

- 教程视频
- 录屏视频
- 技术讲解
- 配置演示
- 本地开发过程录制

## 暂不擅长

- 背景音乐很强的人声视频
- 多人同时说话
- 噪音严重视频
- 需要正式字幕级逐字稿的场景
