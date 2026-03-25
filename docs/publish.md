# Publish to GitHub

当前项目已经完成本地初始化，可以直接进入 GitHub 发布阶段。

## 1. 配置 git 身份（如未配置）

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## 2. 创建 GitHub 仓库

你可以用网页创建一个空仓库，例如：
- `local-video-analysis`

## 3. 绑定远程仓库

```bash
git remote add origin <your-repo-url>
```

例如：

```bash
git remote add origin git@github.com:<owner>/local-video-analysis.git
```

或：

```bash
git remote add origin https://github.com/<owner>/local-video-analysis.git
```

## 4. 推送

```bash
git branch -M main
git push -u origin main
```

## 5. 发布后建议

- 在 GitHub 仓库首页补一句项目描述
- 添加 topics，例如：
  - `video-analysis`
  - `transcription`
  - `whisper`
  - `openclaw`
  - `feishu`
- 后续可以加：
  - issue templates
  - sample benchmark
  - release notes
