# Project ↔ Skill Sync

这个仓库是主项目（source of truth）。

## 先理解：project 和 skill 不是什么关系

它们不是二选一，也不是平级双主仓。

更准确地说：

- **project**：负责开发、测试、版本演进、GitHub 协作
- **skill**：负责在 OpenClaw 运行时里被直接调用

所以推荐心智模型是：

> project 负责“长期建设”，skill 负责“稳定复用”。

## 什么时候用 project

适合：
- 首次部署
- 本地调试
- 改脚本
- 写文档
- 做 smoke test / regression test
- GitHub 提交、评审、版本管理

典型操作：

```bash
cd projects/local-video-analysis
python3 scripts/check_env.py
bash scripts/analyze_video.sh /path/to/video.mp4 30
python3 scripts/export_to_obsidian.py --run-dir ./runs/<video-run> --vault-dir /path/to/vault
```

## 什么时候用 skill

适合：
- 你已经确认这套能力稳定可用
- 你希望在 OpenClaw 里直接触发这条工作流
- 你希望 agent 以后复用的是一个固定入口，而不是临时脚本命令

也就是说：

- project 更适合“建设”
- skill 更适合“调用”

## 推荐原则

- **项目**：优先承载实验、迭代、版本管理、GitHub 协作
- **skill**：优先承载 OpenClaw 内的调用入口

## 推荐部署方式

最推荐的顺序是：

1. 先 clone / 更新项目仓库
2. 在项目目录安装依赖并通过环境检查
3. 先用 project 模式跑通至少一个真实样本
4. 确认输出目录、报告、逐字稿、Obsidian 导出都符合预期
5. 再同步到 `skills/local-video-analysis`
6. 重新打包 `.skill`
7. 在 OpenClaw 里按 skill 方式复用

## 推荐工作方式

1. 先在项目里修改脚本和文档
2. 在项目目录做自检和 smoke test
3. 再把稳定结果同步回 `skills/local-video-analysis`
4. 重新打包 `.skill`

## 为什么这样做

因为：
- 项目更适合长期迭代
- skill 更适合直接调用
- 把项目当主仓库，可以避免 skill 先变、项目后补，导致两边漂移
- 先 project 后 skill，可以显著降低“入口可调用，但底层还不稳”的风险

## 当前同步对象

项目目录：
- `projects/local-video-analysis`

Skill 目录：
- `skills/local-video-analysis`

Skill 包：
- `dist_skills/local-video-analysis.skill`
