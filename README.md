# GitHub 热门项目雷达

每天自动追踪 GitHub 热门项目，过滤噪音、评分，用 DeepSeek 生成中文简介并分门别类整理。

🌐 [在线浏览](https://erick217.github.io/gh-radar/) · [运行记录](https://github.com/erick217/gh-radar/actions/workflows/daily.yml)

👉 [按分类浏览全部项目](docs/index.md) · [最近 7 天新收录](docs/new.md) · [本周增速榜](docs/rising.md)

<!-- radar:start -->

**本周增速 Top 10**（2026-10-29 更新，共收录 68 个，[查看全部分类](docs/index.md)）

| 项目 | 简介 | 分类 | 形态 | 语言 | ⭐ | 7日 | 分数 | 状态 |
|---|---|---|---|---|---|---|---|---|
| [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv) | Debloat any Android or Google TV over Wi-Fi and get an Apple TV-style home. | 未分类/待 AI 处理 |  | Python | 44.8k | +26.1k | 79 |  |
| [storytold/photocraft](https://github.com/storytold/photocraft) | PhotoCraft: An open-source, photo editor written by scratch in pure Rust | 未分类/待 AI 处理 |  | Rust | 74.7k | +18.0k | 79 |  |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | A coding-agent skill for multi-phase security audits with independently verified, machine-readable findings | 未分类/待 AI 处理 |  | JavaScript | 52.4k | +16.0k | 67 |  |
| [deepseek-ai/DeepInfer](https://github.com/deepseek-ai/DeepInfer) | DeepInfer: High-performance, large-scale inference framework for DeepSeek models | 未分类/待 AI 处理 |  | Python | 24.2k | +13.0k | 66 |  |
| [Zagitta/gpu-unlock](https://github.com/Zagitta/gpu-unlock) | Your GeForce runs AI at half speed. This fixes it for 20/30/40 series cards. Up to 2× FP16 / BF16 / TF32 tensor throughput | 未分类/待 AI 处理 |  | C | 12.8k | +8.1k | 72 |  |
| [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) | An agent skill for creating detailed, interactive isometric illustrations of real-world machines and complex systems. Generates polished SVGs with optional WebGL shaders and 3D effects. | 未分类/待 AI 处理 |  | JavaScript | 22.4k | +7.5k | 76 |  |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | The design vocabulary for your coding agent. Steer with polish and bolder, review with critique and audit, catch AI slop before it ships. | 未分类/待 AI 处理 |  | Rust | 94.4k | +7.3k | 77 |  |
| [google-research/harness2](https://github.com/google-research/harness2) |  | 未分类/待 AI 处理 |  | Python | 21.2k | +6.5k | 64 |  |
| [pengchujin/aerial-tv](https://github.com/pengchujin/aerial-tv) | 给国产电视的一块干净桌面：参照 tvOS 设计的开源 Android TV 桌面，没有广告，开机自动接管。A tvOS-style launcher for Xiaomi, TCL and other China-market TVs. | 未分类/待 AI 处理 |  | Kotlin | 7.7k | +6.0k | 75 |  |
| [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) | DeepTutor: Lifelong Personalized Tutoring. https://deeptutor.info/. | 未分类/待 AI 处理 |  | Python | 49.2k | +5.8k | 76 |  |

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
