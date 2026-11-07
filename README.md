# GitHub 热门项目雷达

每天自动追踪 GitHub 热门项目，过滤噪音、评分，用 DeepSeek 生成中文简介并分门别类整理。

🌐 [在线浏览](https://erick217.github.io/gh-radar/) · [运行记录](https://github.com/erick217/gh-radar/actions/workflows/daily.yml)

👉 [按分类浏览全部项目](docs/index.md) · [最近 7 天新收录](docs/new.md) · [本周增速榜](docs/rising.md)

<!-- radar:start -->

**本周增速 Top 10**（2026-11-07 更新，共收录 164 个，[查看全部分类](docs/index.md)）

| 项目 | 简介 | 分类 | 形态 | 语言 | ⭐ | 7日 | 分数 | 状态 |
|---|---|---|---|---|---|---|---|---|
| [storytold/craft-anything](https://github.com/storytold/craft-anything) | 纯 Rust 逆向引擎，用 AI 代理分析网站、应用或游戏并重建类似项目 | AI/Agent | 桌面应用 | Rust | 18.8k | +23.4k | 78 |  |
| [deepseek-ai/dsh-superagent-prototype](https://github.com/deepseek-ai/dsh-superagent-prototype) | 面向单个 GitHub 仓库的主动式编码代理原型，需配合 DeepSeek Harness 使用 | AI/Agent | 其他 | TypeScript | 20.4k | +19.3k | 59 |  |
| [pingdotgg/t3code](https://github.com/pingdotgg/t3code) | 远程控制本机 Claude Code、Codex 等编程代理的桌面与移动端工具 | AI/Agent | 桌面应用 | TypeScript | 50.2k | +17.1k | 97 |  |
| [vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop) | 让 AI Agent 通过系统无障碍树读取并操作桌面应用的 CLI 工具 | AI/Agent | CLI工具 | Rust | 18.3k | +12.9k | 90 |  |
| [ccch1mneyyy/dsh-Go](https://github.com/ccch1mneyyy/dsh-Go) | 把 DeepSeek Harness 装进 Android 手机，本机运行或遥控电脑。 | AI/Agent | 移动应用 | Dart | 13.2k | +11.0k | 80 |  |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 将编码代理变为安全审计员，分阶段产出可验证的漏洞发现。 | 安全/安全工具 | 其他 | JavaScript | 64.5k | +10.0k | 82 |  |
| [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | Python 网页抓取框架，集请求、解析与并发爬虫于一体。 | 数据/数据处理 | 框架 | Python | 99.0k | +9.7k | 90 |  |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 为编码智能体提供可组合的工程技能，涵盖需求对齐、TDD与架构改进。 | AI/Agent | 其他 | Shell | 317.0k | +9.3k | 93 |  |
| [heydamir/unslop](https://github.com/heydamir/unslop) | 把 AI 味浓重的界面逐步改造成有设计感 UI 的 Claude/Codex 技能 | AI/Agent | 其他 | JavaScript | 10.9k | +8.3k | 75 |  |
| [NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) | 为 LLM 与 Agent 构建语义本体和图推理层的 Python 框架 | AI/RAG与知识库 | 框架 | Python | 9.4k | +8.0k | 76 |  |

<!-- radar:end -->

## 工作方式

GitHub Actions 每天运行一次 `python -m radar`：

1. **采集**：GitHub Trending（日榜、周榜）+ Search API（近 30 天新建的高星项目），并刷新已追踪项目的 star 快照
2. **过滤**：丢弃 fork、已归档、README 过短的项目；awesome、教程类归入「学习资源」
3. **评分**：增速 35% + 持续性 20% + 健康度 25% + 实用性 20%，单日暴涨、新建且只有 1 名贡献者的项目会降分
4. **AI 分类**：新项目的 README 发给 DeepSeek，生成中文简介、分类、形态、标签，并判断是否实用；校验分类清单和字段后缓存，每个项目只处理一次
5. **生成页面**：分数达到门槛的项目写入 `docs/`，提交回仓库，再构建并发布到 GitHub Pages

## 手动整理

编辑 [`overrides.yaml`](overrides.yaml)，可以修改分类、标记状态、写笔记、强制收录或隐藏项目，优先级高于 AI 结果。

## 配置

- [`config/settings.yaml`](config/settings.yaml)：采集范围、模型、评分权重、收录门槛
- [`config/taxonomy.yaml`](config/taxonomy.yaml)：分类清单

## 部署

1. 仓库 Settings → Pages → Source，选择 **GitHub Actions**
2. 仓库 Settings → Secrets and variables → Actions，添加 `DEEPSEEK_API_KEY`。未配置时跳过 AI 分类，仍会采集、评分并发布页面，项目暂列为「未分类/待 AI 处理」
3. Actions 页面手动运行一次 `daily-radar`，首次可将 `ai_limit` 填为 `5` 验证少量真实分类，确认 `run` 和 `deploy` 均成功；留空时使用配置中的每轮上限（默认 60 项）
4. 每天北京时间 09:17 开始、至 23:17 每小时检查一次。当天成功发布后，后续定时检查会跳过采集和模型调用；发布失败则后续检查继续补偿。GitHub 定时任务仍可能延迟，不能保证准点
5. 数据提交及页面发布均由该工作流完成，只有页面部署成功后才记录 `data/last-publish.json`；手动运行始终允许立即更新

网页主题自动跟随系统的浅色或深色模式，页面顶部显示北京时间的实际更新时间。

## 本地运行

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export GITHUB_TOKEN=...        # 不设置时 GitHub API 每小时只有 60 次
export DEEPSEEK_API_KEY=...    # 不设置时跳过 AI 分类
.venv/bin/python -m radar
```

AI 默认使用 `deepseek-flash`、`effort: low`，只调用 DeepSeek 官方接口。可用 `--ai-limit 5` 限制本次分类量；`--no-collect --no-ai` 可仅用本地数据重新评分和渲染。
