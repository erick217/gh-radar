# GitHub 热门项目雷达

每天自动追踪 GitHub 热门项目，过滤噪音、评分，用 DeepSeek 生成中文简介并分门别类整理。

🌐 [在线浏览](https://erick217.github.io/gh-radar/) · [运行记录](https://github.com/erick217/gh-radar/actions/workflows/daily.yml)

👉 [按分类浏览全部项目](docs/index.md) · [最近 7 天新收录](docs/new.md) · [本周增速榜](docs/rising.md)

<!-- radar:start -->

**本周增速 Top 10**（2026-10-30 更新，共收录 73 个，[查看全部分类](docs/index.md)）

| 项目 | 简介 | 分类 | 形态 | 语言 | ⭐ | 7日 | 分数 | 状态 |
|---|---|---|---|---|---|---|---|---|
| [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv) | 通过 Wi-Fi 去除 Android TV 臃肿应用并换用简洁启动器。 | 安全/安全工具 | CLI工具 | Python | 45.6k | +24.5k | 83 |  |
| [storytold/photocraft](https://github.com/storytold/photocraft) | 用纯 Rust 编写的开源照片编辑器，支持图层、蒙版与 PSD。 | 多媒体/图像 | 桌面应用 | Rust | 74.9k | +17.5k | 82 |  |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 将编码代理变为安全审计员，分阶段产出可验证的漏洞发现。 | 安全/安全工具 | 其他 | JavaScript | 52.9k | +16.0k | 72 |  |
| [deepseek-ai/DeepInfer](https://github.com/deepseek-ai/DeepInfer) | DeepSeek 大模型高性能离线推理框架 | AI/模型推理与部署 | 框架 | Python | 24.3k | +12.1k | 62 |  |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 为编码代理提供设计审查、打磨与 AI 感检测的 Agent 技能和 CLI | AI/Agent | CLI工具 | Rust | 95.5k | +9.7k | 83 |  |
| [Zagitta/gpu-unlock](https://github.com/Zagitta/gpu-unlock) | 解锁 GeForce 显卡被限制的 Tensor Core 算力，提升 AI 训练与推理速度 | AI/模型推理与部署 | 其他 | C | 13.1k | +7.7k | 76 |  |
| [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) | 用等距 SVG/WebGL 图解机器与复杂系统的 Agent 技能 | AI/Agent | 其他 | JavaScript | 22.6k | +7.2k | 79 |  |
| [google-research/harness2](https://github.com/google-research/harness2) | 递归优化智能体 harness 的框架，自动改进提示、工具与记忆配置 | AI/Agent | 框架 | Python | 21.3k | +6.2k | 60 |  |
| [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) | 基于多智能体与RAG的个性化AI导师和学习工作台 | AI/AI应用 | Web应用 | Python | 50.2k | +5.8k | 81 |  |
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 基于多智能体LLM协作的金融交易分析框架，模拟投研团队分工决策。 | AI/Agent | 框架 | Python | 118.4k | +5.6k | 81 |  |

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
4. 此后每天北京时间 09:17 定时运行（实际启动可能延迟），数据提交及页面发布均由该工作流完成；所需权限已在工作流中声明

## 本地运行

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export GITHUB_TOKEN=...        # 不设置时 GitHub API 每小时只有 60 次
export DEEPSEEK_API_KEY=...    # 不设置时跳过 AI 分类
.venv/bin/python -m radar
```

AI 默认使用 `deepseek-flash`、`effort: low`，只调用 DeepSeek 官方接口。可用 `--ai-limit 5` 限制本次分类量；`--no-collect --no-ai` 可仅用本地数据重新评分和渲染。
