"""把收录的项目生成 Markdown 页面（docs/ 目录，可直接用 GitHub Pages 发布）。"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from datetime import datetime

from .freshness import BEIJING
from .store import DOCS_DIR, ROOT, days_ago, today

SLUGS = {
    "AI": "ai", "开发工具": "devtools", "前端": "frontend", "后端": "backend", "数据": "data",
    "运维与云原生": "ops", "安全": "security", "效率与自托管": "productivity", "多媒体": "media",
    "移动与桌面": "apps", "学习资源": "learning", "其他": "other", "未分类": "unclassified",
}
UNCLASSIFIED = "未分类/待 AI 处理"

# Phosphor-style stroke SVG icons (18x18 / 20x20, currentColor)
PHOSPHOR_ICONS = {
    "arrow_right": '<svg class="radar-icon" width="16" height="16" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M40 128H216M144 56L216 128L144 200" stroke="currentColor" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow_left": '<svg class="radar-icon" width="16" height="16" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M216 128H40M112 56L40 128L112 200" stroke="currentColor" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "funnel": '<svg class="radar-icon" width="20" height="20" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M40 48H216L148 132V208L108 188V132L40 48Z" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "sparkle": '<svg class="radar-icon" width="20" height="20" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M128 32L148 108L224 128L148 148L128 224L108 148L32 128L108 108L128 32Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "clock": '<svg class="radar-icon" width="20" height="20" viewBox="0 0 256 256" fill="none" aria-hidden="true"><circle cx="128" cy="128" r="88" stroke="currentColor" stroke-width="18"/><path d="M128 76V128L168 152" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "cpu": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="48" y="48" width="160" height="160" rx="16" stroke="currentColor" stroke-width="18"/><rect x="92" y="92" width="72" height="72" rx="8" stroke="currentColor" stroke-width="18"/><path d="M96 48V24M160 48V24M96 232V208M160 232V208M48 96H24M48 160H24M232 96H208M232 160H208" stroke="currentColor" stroke-width="18" stroke-linecap="round"/></svg>',
    "terminal": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="32" y="48" width="192" height="160" rx="16" stroke="currentColor" stroke-width="18"/><path d="M72 96L108 128L72 160M124 160H176" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "layout": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="32" y="48" width="192" height="160" rx="16" stroke="currentColor" stroke-width="18"/><path d="M32 104H224M104 104V208" stroke="currentColor" stroke-width="18"/></svg>',
    "database": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><ellipse cx="128" cy="68" rx="80" ry="32" stroke="currentColor" stroke-width="18"/><path d="M48 68V188C48 205.7 83.8 220 128 220C172.2 220 208 205.7 208 188V68" stroke="currentColor" stroke-width="18"/><path d="M48 128C48 145.7 83.8 160 128 160C172.2 160 208 145.7 208 128" stroke="currentColor" stroke-width="18"/></svg>',
    "cloud": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M76 196H188C210.1 196 228 178.1 228 156C228 135.4 212.5 118.4 192.5 116.2C186.1 84.3 158 60 124 60C86.4 60 56 90.4 56 128C56 130.7 56.2 133.4 56.5 136C39.2 139.5 26 154.8 26 173C26 185.7 36.3 196 49 196H76Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "shield": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M48 56L128 32L208 56V120C208 172 172 208 128 224C84 208 48 172 48 120V56Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "lightning": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M144 24L48 144H128L112 232L208 112H128L144 24Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "film": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="32" y="48" width="192" height="160" rx="16" stroke="currentColor" stroke-width="18"/><path d="M104 96L164 128L104 160V96Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "device": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="64" y="28" width="128" height="200" rx="16" stroke="currentColor" stroke-width="18"/><path d="M112 192H144" stroke="currentColor" stroke-width="18" stroke-linecap="round"/></svg>',
    "book": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M48 48H112C120.8 48 128 55.2 128 64V208C128 199.2 120.8 192 112 192H48V48Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/><path d="M208 48H144C135.2 48 128 55.2 128 64V208C128 199.2 135.2 192 144 192H208V48Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "cube": '<svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M128 32L216 80V176L128 224L40 176V80L128 32Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/><path d="M40 80L128 128L216 80M128 128V224" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "plus": '<svg class="radar-icon" width="16" height="16" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M48 128H208M128 48V208" stroke="currentColor" stroke-width="20" stroke-linecap="round"/></svg>',
}

CAT_ICON_KEYS = {
    "AI": "cpu",
    "开发工具": "terminal",
    "前端": "layout",
    "后端": "cube",
    "数据": "database",
    "运维与云原生": "cloud",
    "安全": "shield",
    "效率与自托管": "lightning",
    "多媒体": "film",
    "移动与桌面": "device",
    "学习资源": "book",
    "其他": "cube",
    "未分类": "cube",
}


def resolve(rec: dict, override: dict) -> dict:
    """合并 AI 结果、评分和人工修正，得到最终展示用的条目。"""
    ai = rec.get("ai") or {}
    sc = rec["score"]
    category = override.get("category") or ai.get("category") or UNCLASSIFIED
    if sc["is_resource"] and not override.get("category") and not category.startswith("学习资源"):
        category = "学习资源/资源合集"
    return {
        "full_name": rec["full_name"],
        "url": rec["url"],
        "summary": override.get("summary") or ai.get("summary") or rec.get("description") or "",
        "category": category,
        "form": override.get("form") or ai.get("form") or "",
        "tags": ai.get("tags") or [],
        "language": rec.get("language") or "",
        "stars": rec["stars"][max(rec["stars"])],
        "gain7": sc["gain7"],
        "score": sc["total"],
        "flags": sc["flags"],
        "status": override.get("status") or "",
        "note": override.get("note") or "",
        "similar": override.get("similar") or [],
        "first_seen": rec["first_seen"],
        "pushed_at": rec["pushed_at"],
    }


def _k(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def _num(n: int) -> str:
    return f"{n:,}"


def _cny(v: float) -> str:
    return f"¥{v:.4f}"


def _pct(part: int, total: int) -> str:
    return f"{(part / total * 100):.1f}%" if total > 0 else "0.0%"


def _cell(s: str) -> str:
    return re.sub(r"\s+", " ", s).replace("|", "\\|").strip()


def _table(items: list[dict], show_category: bool = False) -> str:
    head = ["项目", "简介"] + (["分类"] if show_category else []) + ["形态", "语言", "⭐", "7日", "分数", "状态"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for it in items:
        desc = _cell(it["summary"])
        if it["note"]:
            desc += f"<br>备注：{_cell(it['note'])}"
        if it["similar"]:
            desc += "<br>相似：" + "、".join(f"[{s}](https://github.com/{s})" for s in it["similar"])
        if it["flags"]:
            desc += f"<br>提醒：{'、'.join(it['flags'])}"
        row = [f"[{it['full_name']}]({it['url']})", desc]
        if show_category:
            row.append(it["category"])
        row += [it["form"], it["language"], _k(it["stars"]), f"+{_k(it['gain7'])}",
                f"{it['score']:.0f}", it["status"]]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _split(category: str) -> tuple[str, str]:
    top, _, sub = category.partition("/")
    return top, sub or top


def summarize_ai_billing(repos: dict[str, dict]) -> dict:
    """汇总所有仓库记录中的 DeepSeek Token 消耗与计费金额，按日聚合。"""
    now = today()
    stats = {
        "classified_total": 0,
        "billed_count": 0,
        "unbilled_count": 0,
        "prompt_tokens": 0,
        "cache_hit_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost_cny": 0.0,
        "today_date": now,
        "today_billed": 0,
        "today_tokens": 0,
        "today_cost_cny": 0.0,
        "daily": [],
    }
    daily_map: dict[str, dict] = {}

    for rec in repos.values():
        ai = rec.get("ai")
        if not isinstance(ai, dict) or not ai:
            continue
        stats["classified_total"] += 1
        usage = ai.get("usage")
        if not isinstance(usage, dict):
            stats["unbilled_count"] += 1
            continue
        stats["billed_count"] += 1
        p_tok = int(usage.get("prompt_tokens") or 0)
        h_tok = int(usage.get("prompt_cache_hit_tokens") or 0)
        c_tok = int(usage.get("completion_tokens") or 0)
        t_tok = int(usage.get("total_tokens") or (p_tok + c_tok))
        cost = float(usage.get("cost_cny") or 0.0)
        at = str(ai.get("at") or "未知日期")

        stats["prompt_tokens"] += p_tok
        stats["cache_hit_tokens"] += h_tok
        stats["completion_tokens"] += c_tok
        stats["total_tokens"] += t_tok
        stats["cost_cny"] = round(stats["cost_cny"] + cost, 6)

        if at == now:
            stats["today_billed"] += 1
            stats["today_tokens"] += t_tok
            stats["today_cost_cny"] = round(stats["today_cost_cny"] + cost, 6)

        day = daily_map.setdefault(at, {
            "date": at,
            "total_tokens": 0,
            "cost_cny": 0.0,
        })
        day["total_tokens"] += t_tok
        day["cost_cny"] = round(day["cost_cny"] + cost, 6)

    stats["daily"] = sorted(daily_map.values(), key=lambda d: d["date"], reverse=True)
    return stats


def _usage_daily_table(daily: list[dict]) -> str:
    head = ["日期", "总 Tokens", "花费 (¥)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    if not daily:
        lines.append("| 暂无记录 | 0 | ¥0.0000 |")
        return "\n".join(lines)
    for d in daily:
        lines.append("| " + " | ".join([
            d["date"],
            _num(d["total_tokens"]),
            _cny(d["cost_cny"]),
        ]) + " |")
    return "\n".join(lines)


def _usage_summary_text(billing: dict) -> str:
    base = (
        f"累计已记录 {billing['billed_count']} 次 DeepSeek 分类，"
        f"共消耗 {_num(billing['total_tokens'])} tokens，"
        f"合计费用 {_cny(billing['cost_cny'])}"
    )
    if billing["unbilled_count"] > 0:
        return f"{base}（另有 {billing['unbilled_count']} 个早期分类未记录接口 usage）。"
    return f"{base}。"


def _front_matter(title: str, description: str, nav_active: str = "") -> str:
    safe_title = title.replace('"', '\\"')
    safe_desc = description.replace('"', '\\"')
    lines = [
        "---",
        "layout: default",
        f'title: "{safe_title}"',
        f'description: "{safe_desc}"',
    ]
    if nav_active:
        lines.append(f"nav_active: {nav_active}")
    lines.append("---")
    return "\n".join(lines)


def _kpi_card(label: str, value: str, sub: str, accent: str = "") -> str:
    cls = f"radar-kpi{' ' + accent if accent else ''}"
    return (
        f'<div class="{cls}">'
        f'<span class="radar-kpi-label caption-3">{html.escape(label)}</span>'
        f'<strong class="radar-kpi-value heading-4 mono-num">{html.escape(value)}</strong>'
        f'<span class="radar-kpi-sub caption-2">{html.escape(sub)}</span>'
        f'</div>'
    )


def _category_card(top: str, slug: str, subs: dict[str, list]) -> str:
    count = sum(len(v) for v in subs.values())
    icon = PHOSPHOR_ICONS[CAT_ICON_KEYS.get(top, "cube")]
    chips = "".join(
        f'<span class="radar-chip caption-4">{html.escape(sub)} <b class="mono-num">{len(lst)}</b></span>'
        for sub, lst in sorted(subs.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    )
    return (
        f'<a class="radar-cat-card" href="categories/{slug}.html">'
        f'<div class="radar-cat-head">'
        f'<span class="radar-cat-title title-3">{icon}<span>{html.escape(top)}</span></span>'
        f'<span class="radar-cat-count caption-3 mono-num">{count}</span>'
        f'</div>'
        f'<div class="radar-cat-chips">{chips}</div>'
        f'</a>'
    )


def _hero_preview_item(item: dict) -> str:
    return (
        f'<a class="radar-preview-item" href="{html.escape(item["url"])}" target="_blank" rel="noopener">'
        f'<div class="radar-preview-meta">'
        f'<span class="body-4">{html.escape(item["full_name"])}</span>'
        f'<span class="radar-preview-desc caption-2">{html.escape(item["summary"])}</span>'
        f'</div>'
        f'<div class="radar-preview-stats">'
        f'<span class="radar-pill caption-3 is-gain mono-num">+{_k(item["gain7"])}</span>'
        f'<span class="radar-pill caption-3 is-score-high mono-num">{item["score"]:.0f}</span>'
        f'</div>'
        f'</a>'
    )


def _tagline_reveal_html() -> str:
    tokens = [
        "好项目", "不该", "埋没在", "刷星噪音", "里，",
        "<br>",
        "每天", "两分钟，", "只看", "真正", "值得上手的", "开源工具。",
    ]
    rendered = "".join(
        "<br>" if t == "<br>" else f'<span class="radar-reveal-word">{html.escape(t)}</span>'
        for t in tokens
    )
    return (
        '<section class="radar-tagline-section" aria-label="核心主张">'
        f'<p class="radar-tagline-text heading-2">{rendered}</p>'
        '</section>'
    )


def _render_index_page(
    items: list[dict],
    total_tracked: int,
    rising: list[dict],
    cat_cards: list[str],
    billing: dict,
    updated_str: str,
) -> str:
    preview_rows = "".join(_hero_preview_item(it) for it in rising[:3])
    hero_html = (
        '<section class="radar-hero">'
        '<div class="radar-hero-content">'
        f'<span class="radar-badge caption-3"><span class="radar-proof-dot"></span><span>更新于 {html.escape(updated_str)}（北京时间）</span></span>'
        '<h1 class="heading-1 radar-hero-title">过滤 GitHub 榜单噪音，<br>直达高价值开源项目</h1>'
        '<p class="body-3 radar-hero-sub">每天自动采集 GitHub Trending 与高星新仓，通过四维评分模型剔除刷星与空壳仓库，并由 DeepSeek 生成中文简介与精细分类。</p>'
        '<div class="radar-hero-cta">'
        f'<a class="radar-btn is-primary button-md" href="rising.html"><span>查看本周增速榜</span>{PHOSPHOR_ICONS["arrow_right"]}</a>'
        '</div>'
        '<div class="radar-proof-row caption-2">'
        f'<span class="radar-proof-item">已收录 <strong class="mono-num">{len(items)}</strong> 个项目</span>'
        f'<span class="radar-proof-item">追踪 <strong class="mono-num">{total_tracked}</strong> 个仓库</span>'
        f'<span class="radar-proof-item">累计 API 花费 <strong class="mono-num">{_cny(billing["cost_cny"])}</strong></span>'
        '</div>'
        '</div>'
        '<aside class="radar-preview-card" aria-label="本周增速前三预览">'
        '<div class="radar-preview-head">'
        '<span class="title-4">本周增速前三</span>'
        '<span class="caption-4 mono-num">实时快照</span>'
        '</div>'
        f'<div class="radar-preview-list">{preview_rows}</div>'
        '</aside>'
        '</section>'
    )

    benefits_html = (
        '<section class="radar-section radar-reveal">'
        '<div class="radar-section-head">'
        '<div>'
        '<h2 class="heading-4">为什么看这份雷达而不是直接刷 Trending</h2>'
        '<p class="body-3 radar-section-sub">把人工筛选与阅读长篇英文文档的时间省下来，只保留真实可用且持续增长的项目。</p>'
        '</div>'
        '</div>'
        '<div class="radar-grid-3">'
        '<article class="radar-card">'
        f'<div class="radar-icon-box">{PHOSPHOR_ICONS["funnel"]}</div>'
        '<h3 class="title-2">硬过滤与防刷星降权</h3>'
        '<p class="body-6 radar-card-desc">自动排除 Fork、归档及 README 少于 200 字符的仓库；对单日暴涨超 80% 或单人新仓自动降分。</p>'
        '</article>'
        '<article class="radar-card">'
        f'<div class="radar-icon-box">{PHOSPHOR_ICONS["sparkle"]}</div>'
        '<h3 class="title-2">DeepSeek 中文摘要与形态标注</h3>'
        '<p class="body-6 radar-card-desc">提炼 40 字以内客观中文简介，标注项目形态、12 个主分类与可运行实用性，且每个项目只分析一次。</p>'
        '</article>'
        '<article class="radar-card">'
        f'<div class="radar-icon-box">{PHOSPHOR_ICONS["clock"]}</div>'
        '<h3 class="title-2">连续快照与每日透明计费</h3>'
        '<p class="body-6 radar-card-desc">连续 45 天记录活跃仓库 Star 曲线，并在页面公开每日 DeepSeek Token 用量与人民币花费。</p>'
        '</article>'
        '</div>'
        '</section>'
    )

    how_html = (
        '<section class="radar-section radar-reveal">'
        '<div class="radar-section-head">'
        '<div>'
        '<h2 class="heading-4">三步完成每日筛选与发布</h2>'
        '<p class="body-3 radar-section-sub">全部流程由 GitHub Actions 自动运行并归档到仓库数据目录，零人工维护成本。</p>'
        '</div>'
        '</div>'
        '<div class="radar-grid-3">'
        '<article class="radar-card">'
        '<span class="caption-3 mono-num radar-step-num">01 / 采集</span>'
        '<h3 class="title-2">拉取榜单与高星新仓</h3>'
        '<p class="body-6 radar-card-desc">抓取日榜、周榜及 30 天内新建超 300 星仓库，同步刷新已收录项目的 Star 快照。</p>'
        '</article>'
        '<article class="radar-card">'
        '<span class="caption-3 mono-num radar-step-num">02 / 评分</span>'
        '<h3 class="title-2">四维权重模型打分</h3>'
        '<p class="body-6 radar-card-desc">综合 7 日增速（35%）、健康度（25%）、持续性（20%）与实用性（20%），达 55 分进入收录。</p>'
        '</article>'
        '<article class="radar-card">'
        '<span class="caption-3 mono-num radar-step-num">03 / 发布</span>'
        '<h3 class="title-2">生成分类页与静态站点</h3>'
        '<p class="body-6 radar-card-desc">自动输出分类索引、7 日新收录、增速榜及每日 Usage 表格，并构建发布到 GitHub Pages。</p>'
        '</article>'
        '</div>'
        '</section>'
    )

    cats_html = (
        '<section class="radar-section radar-reveal">'
        '<div class="radar-section-head">'
        '<div>'
        '<h2 class="heading-4">按技术领域浏览全部项目</h2>'
        f'<p class="body-3 radar-section-sub">当前共收录 {len(items)} 个项目，覆盖 {len(cat_cards)} 个一级分类，支持站内搜索、语言筛选与表头排序。</p>'
        '</div>'
        f'<a class="radar-btn button-sm" href="new.html"><span>查看 7 日新收录</span>{PHOSPHOR_ICONS["arrow_right"]}</a>'
        '</div>'
        f'<div class="radar-cat-grid">{"".join(cat_cards)}</div>'
        '</section>'
    )

    faqs = [
        ("数据多久更新一次，什么时间刷新？", "GitHub Actions 每天北京时间 09:17 至 23:17 每小时检查一次。当天首次成功发布后自动跳过后续时段，避免重复采集与消耗模型额度。"),
        ("如何避免刷星仓库或纯宣传页上榜？", "评分模型会检查近 7 天单日增量占比，若单日占 80% 以上会扣 10 分；新建不足 7 天且只有 1 名贡献者扣 15 分；README 不足 200 字符直接排除。"),
        ("接入 DeepSeek API 每天大概花多少钱？", "系统使用 deepseek-flash 低推理模式，且每个仓库只分析一次并永久缓存结果。日常每天仅处理新增项目，花费通常在数分钱人民币以内。"),
        ("每日 Usage 表格里的数字是估算还是真实返回？", "全部来自 DeepSeek Chat Completions 接口实际返回的 total_tokens 字段，并按 settings.yaml 配置的人民币单价折算花费。"),
        ("为什么页面提示部分早期项目未记录 usage？", "在接入 Usage 计费统计之前已完成分类的仓库 JSON 中没有保存旧版返回用量，这部分项目不会再重复调用接口，仅对新项目开始记录。"),
        ("如何手工修正分类或自己 Fork 部署一份？", "编辑根目录 overrides.yaml 可覆盖分类、备注或强制置顶/隐藏。Fork 仓库后在 Settings 中启用 GitHub Actions 部署 Pages 并添加 DEEPSEEK_API_KEY 即可。"),
    ]
    faq_items = "".join(
        f'<details class="radar-faq-item"><summary class="title-3"><span>{html.escape(q)}</span>{PHOSPHOR_ICONS["plus"]}</summary><p class="body-6 radar-faq-answer">{html.escape(a)}</p></details>'
        for q, a in faqs
    )
    faq_html = (
        '<section class="radar-section radar-reveal">'
        '<div class="radar-section-head">'
        '<div>'
        '<h2 class="heading-4">常见问题</h2>'
        '<p class="body-3 radar-section-sub">关于筛选规则、DeepSeek 计费统计与自部署的常见说明。</p>'
        '</div>'
        '</div>'
        f'<div class="radar-faq-list">{faq_items}</div>'
        '</section>'
    )

    final_cta_html = (
        '<section class="radar-section radar-reveal">'
        '<div class="radar-final-cta">'
        '<h2 class="heading-3">立即浏览本周增速最快的开源项目</h2>'
        '<p class="body-3">按近 7 天真实 Star 增量排序，结合语言筛选与关键字搜索，快速找到能直接落地到工作流的工具。</p>'
        f'<a class="radar-btn is-primary button-md" href="rising.html"><span>查看本周增速榜</span>{PHOSPHOR_ICONS["arrow_right"]}</a>'
        '</div>'
        '</section>'
    )

    parts = [
        _front_matter(
            "概览",
            f"每日追踪 GitHub 热门实用开源项目，当前收录 {len(items)} 个项目，附 DeepSeek 每日用量统计。",
            nav_active="index",
        ),
        "",
        hero_html,
        "",
        benefits_html,
        "",
        _tagline_reveal_html(),
        "",
        how_html,
        "",
        cats_html,
        "",
        '<section class="radar-section radar-reveal">',
        '<div class="radar-section-head">',
        '<div>',
        '<h2 class="heading-4">DeepSeek 每日 Usage 与花费</h2>',
        '<p class="body-3 radar-section-sub">仅保留每日总 Token 与人民币花费，方便快速核对账单。</p>',
        '</div>',
        f'<a class="radar-btn button-sm" href="usage.html"><span>查看全部日期</span>{PHOSPHOR_ICONS["arrow_right"]}</a>',
        '</div>',
        '</section>',
        "",
        _usage_daily_table(billing["daily"][:7]),
        "",
        f'<p class="caption-2 radar-usage-summary">{html.escape(_usage_summary_text(billing))}</p>',
        "",
        faq_html,
        "",
        final_cta_html,
        "",
    ]
    return "\n".join(parts)


def _render_usage_page(billing: dict, updated_str: str) -> str:
    hit_rate = _pct(billing["cache_hit_tokens"], billing["prompt_tokens"])
    kpis = "".join([
        _kpi_card("累计花费", _cny(billing["cost_cny"]), f"今日 {_cny(billing['today_cost_cny'])}", accent="is-cost"),
        _kpi_card("累计 Token", _k(billing["total_tokens"]), f"已记录 {billing['billed_count']} 次分类"),
        _kpi_card("缓存命中率", hit_rate, f"命中 {_k(billing['cache_hit_tokens'])} / 输入 {_k(billing['prompt_tokens'])}"),
        _kpi_card("已记录天数", str(len(billing["daily"])), f"历史结果永久缓存不重复扣费"),
    ])
    parts = [
        _front_matter(
            "每日 Usage",
            "DeepSeek API 每日 Token 消耗与人民币花费简表。",
            nav_active="usage",
        ),
        "",
        '<section class="radar-page-head">',
        f'<a class="radar-back-link caption-1" href="index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
        '<h1 class="heading-3">DeepSeek 每日 Usage 与花费</h1>',
        f'<p class="body-3 radar-page-desc">更新于 {html.escape(updated_str)}（北京时间） · 仅针对新增或未缓存项目调用 DeepSeek API，按实际返回总 Token 与单价每日汇总。</p>',
        '</section>',
        "",
        f'<div class="radar-stats-grid">{kpis}</div>',
        "",
        '<h2 class="heading-5 radar-sub-heading">每日用量统计</h2>',
        "",
        _usage_daily_table(billing["daily"]),
        "",
        f'<p class="caption-2 radar-usage-summary">{html.escape(_usage_summary_text(billing))}</p>',
        "",
    ]
    return "\n".join(parts)


def render(repos: dict[str, dict], overrides: dict, settings: dict | None = None) -> dict:
    items = [resolve(r, overrides.get(n) or {}) for n, r in repos.items()
             if (r.get("score") or {}).get("included")]
    by_top: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for it in items:
        top, sub = _split(it["category"])
        by_top[top][sub].append(it)

    (DOCS_DIR / "categories").mkdir(parents=True, exist_ok=True)
    for old in (DOCS_DIR / "categories").glob("*.md"):
        old.unlink()

    order = [t for t in SLUGS if t in by_top] + sorted(t for t in by_top if t not in SLUGS)
    cat_cards = []
    for i, top in enumerate(order):
        slug = SLUGS.get(top, f"cat{i}")
        subs = by_top[top]
        count = sum(len(v) for v in subs.values())
        cat_cards.append(_category_card(top, slug, subs))
        parts = [
            _front_matter(
                top,
                f"{top}分类下的热门开源项目，共收录 {count} 个。",
            ),
            "",
            '<section class="radar-page-head">',
            f'<a class="radar-back-link caption-1" href="../index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
            f'<h1 class="heading-3">{html.escape(top)}</h1>',
            f'<p class="body-3 radar-page-desc">共收录 {count} 个项目，各子分类按综合评分由高到低排列。</p>',
            '</section>',
            "",
        ]
        for sub, lst in sorted(subs.items(), key=lambda kv: -len(kv[1])):
            lst.sort(key=lambda x: -x["score"])
            parts.append(f'<h2 class="heading-5 radar-sub-heading">{html.escape(sub)}（{len(lst)}）</h2>\n\n{_table(lst)}\n')
        (DOCS_DIR / "categories" / f"{slug}.md").write_text("\n".join(parts), encoding="utf-8")

    week_ago = days_ago(7)
    new = sorted((x for x in items if x["first_seen"] >= week_ago), key=lambda x: -x["score"])
    rising = sorted(items, key=lambda x: -x["gain7"])[:30]
    billing = summarize_ai_billing(repos)
    updated_str = f"{datetime.now(BEIJING):%Y-%m-%d %H:%M}"

    (DOCS_DIR / "index.md").write_text(
        _render_index_page(items, len(repos), rising, cat_cards, billing, updated_str),
        encoding="utf-8",
    )

    new_page = [
        _front_matter(
            "最近 7 天新收录",
            f"近 7 天新进入 GitHub 热门项目雷达的 {len(new)} 个开源项目。",
            nav_active="new",
        ),
        "",
        '<section class="radar-page-head">',
        f'<a class="radar-back-link caption-1" href="index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
        f'<h1 class="heading-3">最近 7 天新收录（{len(new)}）</h1>',
        f'<p class="body-3 radar-page-desc">更新于 {html.escape(updated_str)}（北京时间） · 按综合评分由高到低排序，支持搜索、语言筛选与点击表头排序。</p>',
        '</section>',
        "",
        _table(new, True),
        "",
    ]
    (DOCS_DIR / "new.md").write_text("\n".join(new_page), encoding="utf-8")

    rising_page = [
        _front_matter(
            "本周增速榜",
            f"最近 7 天 Star 增速排名前 {len(rising)} 的开源项目。",
            nav_active="rising",
        ),
        "",
        '<section class="radar-page-head">',
        f'<a class="radar-back-link caption-1" href="index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
        f'<h1 class="heading-3">本周增速榜 Top {len(rising)}</h1>',
        f'<p class="body-3 radar-page-desc">更新于 {html.escape(updated_str)}（北京时间） · 按最近 7 天 Star 增量排序，支持搜索、语言筛选与点击表头排序。</p>',
        '</section>',
        "",
        _table(rising, True),
        "",
    ]
    (DOCS_DIR / "rising.md").write_text("\n".join(rising_page), encoding="utf-8")

    (DOCS_DIR / "usage.md").write_text(_render_usage_page(billing, updated_str), encoding="utf-8")
    (DOCS_DIR / "data.json").write_text(
        json.dumps(sorted(items, key=lambda x: -x["score"]), ensure_ascii=False, indent=1), encoding="utf-8")
    (DOCS_DIR / "usage.json").write_text(
        json.dumps({
            "billed_count": billing["billed_count"],
            "unbilled_count": billing["unbilled_count"],
            "total_tokens": billing["total_tokens"],
            "cost_cny": billing["cost_cny"],
            "daily": billing["daily"],
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    _update_readme(rising[:10], len(items), billing)
    return {
        "included": len(items),
        "new_7d": len(new),
        "billed_repos": billing["billed_count"],
        "total_tokens": billing["total_tokens"],
        "cost_cny": billing["cost_cny"],
    }


def _update_readme(top: list[dict], total: int, billing: dict) -> None:
    path = ROOT / "README.md"
    start, end = "<!-- radar:start -->", "<!-- radar:end -->"
    text = path.read_text(encoding="utf-8")
    block = (
        f"{start}\n\n"
        f"**DeepSeek 每日 Usage**（[查看完整记录](docs/usage.md)）\n\n"
        f"{_usage_daily_table(billing['daily'][:7])}\n\n"
        f"> {_usage_summary_text(billing)}\n\n"
        f"**本周增速 Top 10**（{today()} 更新，共收录 {total} 个，[查看全部分类](docs/index.md)）\n\n"
        f"{_table(top, True)}\n\n"
        f"{end}"
    )
    text = re.sub(re.escape(start) + ".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    path.write_text(text, encoding="utf-8")
