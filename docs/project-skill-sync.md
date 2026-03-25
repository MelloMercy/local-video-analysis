# Project ↔ Skill Sync

这个仓库是主项目（source of truth）。

## 推荐原则

- **项目**：优先承载实验、迭代、版本管理、GitHub 协作
- **skill**：优先承载 OpenClaw 内的调用入口

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

## 当前同步对象

项目目录：
- `projects/local-video-analysis`

Skill 目录：
- `skills/local-video-analysis`

Skill 包：
- `dist_skills/local-video-analysis.skill`
