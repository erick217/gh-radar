# GitHub 热门项目雷达

每天自动追踪 GitHub 热门项目，过滤噪音、评分，用 Claude 生成中文简介并分门别类整理。

👉 [按分类浏览全部项目](docs/index.md) · [最近 7 天新收录](docs/new.md) · [本周增速榜](docs/rising.md)

<!-- radar:start -->
<!-- radar:end -->

## 工作方式

GitHub Actions 每天运行一次 `python -m radar`：

1. **采集**：GitHub Trending（日榜、周榜）+ Search API（近 30 天新建的高星项目），并刷新已追踪项目的 star 快照
2. **过滤**：丢弃 fork、已归档、README 过短的项目；awesome、教程类归入「学习资源」
3. **评分**：增速 35% + 持续性 20% + 健康度 25% + 实用性 20%，单日暴涨、新建且只有 1 名贡献者的项目会降分
4. **AI 分类**：新项目的 README 发给 Claude，生成中文简介、分类、形态、标签，并判断是否实用；每个项目只处理一次
5. **生成页面**：分数达到门槛的项目写入 `docs/`，提交回仓库

## 手动整理

编辑 [`overrides.yaml`](overrides.yaml)，可以修改分类、标记状态、写笔记、强制收录或隐藏项目，优先级高于 AI 结果。

## 配置

- [`config/settings.yaml`](config/settings.yaml)：采集范围、模型、评分权重、收录门槛
- [`config/taxonomy.yaml`](config/taxonomy.yaml)：分类清单

## 部署

1. 仓库 Settings → Secrets and variables → Actions，添加 `ANTHROPIC_API_KEY`
2. Settings → Actions → General → Workflow permissions，选 **Read and write permissions**
3. Actions 页面手动运行一次 `daily-radar`
4. 可选：Settings → Pages，Source 选 `main` 分支的 `/docs` 目录

## 本地运行

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export GITHUB_TOKEN=...        # 不设置时 GitHub API 每小时只有 60 次
export ANTHROPIC_API_KEY=...   # 不设置时跳过 AI 分类
.venv/bin/python -m radar
```
