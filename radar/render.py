"""把收录的项目生成 Markdown 页面（docs/ 目录，可直接用 GitHub Pages 发布）。"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from datetime import datetime

from .classify import DEFAULT_PRICING
from .freshness import BEIJING
from .store import DOCS_DIR, ROOT, days_ago, today

SLUGS = {
    "AI": "ai", "开发工具": "devtools", "前端": "frontend", "后端": "backend", "数据": "data",
    "运维与云原生": "ops", "安全": "security", "效率与自托管": "productivity", "多媒体": "media",
    "移动与桌面": "apps", "学习资源": "learning", "其他": "other", "未分类": "unclassified",
}
CAT_ICONS = {
    "AI": "🤖",
    "开发工具": "🛠️",
    "前端": "🎨",
    "后端": "⚙️",
    "数据": "📊",
    "运维与云原生": "☁️",
    "安全": "🔒",
    "效率与自托管": "⚡",
    "多媒体": "🎬",
    "移动与桌面": "📱",
    "学习资源": "📚",
    "其他": "📦",
    "未分类": "❓",
}
UNCLASSIFIED = "未分类/待 AI 处理"


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


def _tokens_sub(total: int, sub: int, label: str) -> str:
    if sub > 0:
        return f"{_num(total)}（{label} {_num(sub)}）"
    return _num(total)


def _cell(s: str) -> str:
    return re.sub(r"\s+", " ", s).replace("|", "\\|").strip()


def _table(items: list[dict], show_category: bool = False) -> str:
    head = ["项目", "简介"] + (["分类"] if show_category else []) + ["形态", "语言", "⭐", "7日", "分数", "状态"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for it in items:
        desc = _cell(it["summary"])
        if it["note"]:
            desc += f"<br>📝 {_cell(it['note'])}"
        if it["similar"]:
            desc += "<br>相似：" + "、".join(f"[{s}](https://github.com/{s})" for s in it["similar"])
        if it["flags"]:
            desc += f"<br>⚠️ {'、'.join(it['flags'])}"
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
    """汇总所有仓库记录中的 DeepSeek Token 消耗与计费金额。"""
    now = today()
    stats = {
        "classified_total": 0,
        "billed_count": 0,
        "unbilled_count": 0,
        "prompt_tokens": 0,
        "cache_hit_tokens": 0,
        "cache_miss_tokens": 0,
        "completion_tokens": 0,
        "reasoning_tokens": 0,
        "total_tokens": 0,
        "cost_cny": 0.0,
        "today_date": now,
        "today_billed": 0,
        "today_prompt_tokens": 0,
        "today_cache_hit_tokens": 0,
        "today_cache_miss_tokens": 0,
        "today_completion_tokens": 0,
        "today_reasoning_tokens": 0,
        "today_tokens": 0,
        "today_cost_cny": 0.0,
        "daily": [],
        "records": [],
    }
    daily_map: dict[str, dict] = {}
    records: list[dict] = []

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
        m_tok = int(usage["prompt_cache_miss_tokens"]) if "prompt_cache_miss_tokens" in usage else max(0, p_tok - h_tok)
        c_tok = int(usage.get("completion_tokens") or 0)
        r_tok = int(usage.get("reasoning_tokens") or 0)
        t_tok = int(usage.get("total_tokens") or (p_tok + c_tok))
        cost = float(usage.get("cost_cny") or 0.0)
        at = str(ai.get("at") or "未知日期")

        stats["prompt_tokens"] += p_tok
        stats["cache_hit_tokens"] += h_tok
        stats["cache_miss_tokens"] += m_tok
        stats["completion_tokens"] += c_tok
        stats["reasoning_tokens"] += r_tok
        stats["total_tokens"] += t_tok
        stats["cost_cny"] = round(stats["cost_cny"] + cost, 6)

        if at == now:
            stats["today_billed"] += 1
            stats["today_prompt_tokens"] += p_tok
            stats["today_cache_hit_tokens"] += h_tok
            stats["today_cache_miss_tokens"] += m_tok
            stats["today_completion_tokens"] += c_tok
            stats["today_reasoning_tokens"] += r_tok
            stats["today_tokens"] += t_tok
            stats["today_cost_cny"] = round(stats["today_cost_cny"] + cost, 6)

        day = daily_map.setdefault(at, {
            "date": at,
            "count": 0,
            "prompt_tokens": 0,
            "cache_hit_tokens": 0,
            "cache_miss_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0,
            "cost_cny": 0.0,
        })
        day["count"] += 1
        day["prompt_tokens"] += p_tok
        day["cache_hit_tokens"] += h_tok
        day["cache_miss_tokens"] += m_tok
        day["completion_tokens"] += c_tok
        day["reasoning_tokens"] += r_tok
        day["total_tokens"] += t_tok
        day["cost_cny"] = round(day["cost_cny"] + cost, 6)

        records.append({
            "date": at,
            "full_name": rec.get("full_name") or "",
            "url": rec.get("url") or f"https://github.com/{rec.get('full_name', '')}",
            "model": ai.get("model") or "deepseek-flash",
            "prompt_tokens": p_tok,
            "cache_hit_tokens": h_tok,
            "cache_miss_tokens": m_tok,
            "completion_tokens": c_tok,
            "reasoning_tokens": r_tok,
            "total_tokens": t_tok,
            "cost_cny": round(cost, 6),
        })

    stats["daily"] = sorted(daily_map.values(), key=lambda d: d["date"], reverse=True)
    stats["records"] = sorted(records, key=lambda r: (r["date"], r["cost_cny"], r["full_name"]), reverse=True)
    return stats


def _usage_overview_table(billing: dict) -> str:
    head = ["周期", "调用次数", "输入 Tokens", "缓存命中", "命中率", "缓存未命中", "输出 Tokens（思维链）", "总 Tokens", "花费 (¥)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    rows = [
        (
            f"今日（{billing['today_date']}）",
            billing["today_billed"],
            billing["today_prompt_tokens"],
            billing["today_cache_hit_tokens"],
            billing["today_cache_miss_tokens"],
            billing["today_completion_tokens"],
            billing["today_reasoning_tokens"],
            billing["today_tokens"],
            billing["today_cost_cny"],
        ),
        (
            "累计（已记录）",
            billing["billed_count"],
            billing["prompt_tokens"],
            billing["cache_hit_tokens"],
            billing["cache_miss_tokens"],
            billing["completion_tokens"],
            billing["reasoning_tokens"],
            billing["total_tokens"],
            billing["cost_cny"],
        ),
    ]
    for label, count, prompt_t, hit_t, miss_t, comp_t, reason_t, total_t, cost in rows:
        lines.append("| " + " | ".join([
            label,
            _num(count),
            _num(prompt_t),
            _num(hit_t),
            _pct(hit_t, prompt_t),
            _num(miss_t),
            _tokens_sub(comp_t, reason_t, "含思维链"),
            _num(total_t),
            _cny(cost),
        ]) + " |")
    return "\n".join(lines)


def _usage_daily_table(billing: dict) -> str:
    head = ["日期", "调用次数", "输入 Tokens", "缓存命中", "命中率", "缓存未命中", "输出 Tokens（思维链）", "总 Tokens", "花费 (¥)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    if not billing["daily"]:
        lines.append("| 暂无记录 | 0 | 0 | 0 | 0.0% | 0 | 0 | 0 | ¥0.0000 |")
        return "\n".join(lines)
    for d in billing["daily"]:
        lines.append("| " + " | ".join([
            d["date"],
            _num(d["count"]),
            _num(d["prompt_tokens"]),
            _num(d["cache_hit_tokens"]),
            _pct(d["cache_hit_tokens"], d["prompt_tokens"]),
            _num(d["cache_miss_tokens"]),
            _tokens_sub(d["completion_tokens"], d["reasoning_tokens"], "含思维链"),
            _num(d["total_tokens"]),
            _cny(d["cost_cny"]),
        ]) + " |")
    return "\n".join(lines)


def _usage_records_table(billing: dict) -> str:
    head = ["日期", "项目", "模型", "输入", "缓存命中", "缓存未命中", "输出（思维链）", "总 Tokens", "花费 (¥)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    if not billing["records"]:
        lines.append("| — | 暂无已记录 usage 的项目 | — | 0 | 0 | 0 | 0 | 0 | ¥0.0000 |")
        return "\n".join(lines)
    for r in billing["records"]:
        lines.append("| " + " | ".join([
            r["date"],
            f"[{_cell(r['full_name'])}]({r['url']})",
            _cell(str(r["model"])),
            _num(r["prompt_tokens"]),
            _num(r["cache_hit_tokens"]),
            _num(r["cache_miss_tokens"]),
            _tokens_sub(r["completion_tokens"], r["reasoning_tokens"], "思维链"),
            _num(r["total_tokens"]),
            _cny(r["cost_cny"]),
        ]) + " |")
    return "\n".join(lines)


def _usage_pricing_table(pricing: dict) -> str:
    rates = {**DEFAULT_PRICING, **(pricing or {})}
    lines = [
        "| 计费项 | 单价（元 / 1M Tokens） | 说明 |",
        "|---|---|---|",
        f"| 输入（缓存命中） | ¥{float(rates['input_cache_hit']):.2f} | 复用固定 System Prompt 与 JSON Schema |",
        f"| 输入（缓存未命中） | ¥{float(rates['input_cache_miss']):.2f} | 仓库元数据与 README 内容 |",
        f"| 输出（含思维链） | ¥{float(rates['output']):.2f} | 模型推理与 JSON 结构化输出 |",
    ]
    return "\n".join(lines)


def _nav(active: str, prefix: str = "") -> str:
    links = [
        ("index", "概览", f"{prefix}index.html"),
        ("new", "7日新收录", f"{prefix}new.html"),
        ("rising", "本周增速榜", f"{prefix}rising.html"),
        ("usage", "Usage 计费", f"{prefix}usage.html"),
    ]
    nav_items = "".join(
        f'<a class="radar-nav-link{" is-active" if key == active else ""}" href="{href}">{label}</a>'
        for key, label, href in links
    )
    return (
        '<nav class="radar-nav" aria-label="主导航">'
        f'<a class="radar-brand" href="{prefix}index.html">📡 GitHub 热门项目雷达</a>'
        f'<div class="radar-nav-links">{nav_items}</div>'
        '<div class="radar-nav-actions">'
        '<a class="radar-nav-ext" href="https://github.com/erick217/gh-radar" target="_blank" rel="noopener">GitHub ↗</a>'
        '</div>'
        '</nav>'
    )


def _kpi_card(label: str, value: str, sub: str, href: str | None = None, accent: str = "") -> str:
    cls = f"radar-kpi{' ' + accent if accent else ''}"
    inner = (
        f'<span class="radar-kpi-label">{html.escape(label)}</span>'
        f'<strong class="radar-kpi-value">{html.escape(value)}</strong>'
        f'<span class="radar-kpi-sub">{html.escape(sub)}</span>'
    )
    if href:
        return f'<a class="{cls} is-link" href="{href}">{inner}</a>'
    return f'<div class="{cls}">{inner}</div>'


def _category_card(top: str, slug: str, subs: dict[str, list]) -> str:
    count = sum(len(v) for v in subs.values())
    icon = CAT_ICONS.get(top, "📁")
    chips = "".join(
        f'<span class="radar-chip">{html.escape(sub)} <b>{len(lst)}</b></span>'
        for sub, lst in sorted(subs.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    )
    return (
        f'<a class="radar-cat-card" href="categories/{slug}.html">'
        f'<div class="radar-cat-head">'
        f'<span class="radar-cat-title">{icon} {html.escape(top)}</span>'
        f'<span class="radar-cat-count">{count}</span>'
        f'</div>'
        f'<div class="radar-cat-chips">{chips}</div>'
        f'</a>'
    )


def _render_usage_page(billing: dict, pricing: dict, updated_str: str) -> str:
    hit_rate = _pct(billing["cache_hit_tokens"], billing["prompt_tokens"])
    kpis = "".join([
        _kpi_card("累计花费", _cny(billing["cost_cny"]), f"今日 {_cny(billing['today_cost_cny'])}", accent="is-cost"),
        _kpi_card("累计 Token", _k(billing["total_tokens"]), f"已记录 {billing['billed_count']} 次分类"),
        _kpi_card("缓存命中率", hit_rate, f"命中 {_k(billing['cache_hit_tokens'])} / 输入 {_k(billing['prompt_tokens'])}"),
        _kpi_card("输出 Token", _k(billing["completion_tokens"]), f"含思维链 {_k(billing['reasoning_tokens'])}"),
    ])
    note = ""
    if billing["unbilled_count"] > 0:
        note = f"> 注：另有 **{billing['unbilled_count']}** 个早期项目在接入计费统计前完成分类，未包含在上方接口 usage 明细中。\n\n"
    parts = [
        _nav("usage"),
        "",
        '<header class="radar-page-head">'
        '<div class="radar-page-kicker">DeepSeek API 账单与监控</div>'
        '<h1>DeepSeek Token 用量与花费</h1>'
        f'<p class="radar-page-desc">更新于 {html.escape(updated_str)}（北京时间） · 仅针对新增或未缓存项目调用 DeepSeek API，历史结果永久缓存不重复扣费。</p>'
        '</header>',
        "",
        f'<div class="radar-stats-grid">{kpis}</div>',
        "",
        "## 用量概览\n",
        _usage_overview_table(billing),
        "",
        note + "## 每日用量统计\n",
        _usage_daily_table(billing),
        "",
        f"## 单项目调用明细（{billing['billed_count']}）\n",
        _usage_records_table(billing),
        "",
        "## 计费单价参考\n",
        _usage_pricing_table(pricing),
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
        icon = CAT_ICONS.get(top, "📁")
        parts = [
            _nav("", prefix="../"),
            "",
            '<header class="radar-page-head">'
            '<div class="radar-page-kicker"><a href="../index.html">← 返回首页概览</a></div>'
            f'<h1>{icon} {html.escape(top)}</h1>'
            f'<p class="radar-page-desc">共收录 <strong>{count}</strong> 个项目，各子分类按综合评分由高到低排列。</p>'
            '</header>',
            "",
        ]
        for sub, lst in sorted(subs.items(), key=lambda kv: -len(kv[1])):
            lst.sort(key=lambda x: -x["score"])
            parts.append(f"## {sub}（{len(lst)}）\n\n{_table(lst)}\n")
        (DOCS_DIR / "categories" / f"{slug}.md").write_text("\n".join(parts), encoding="utf-8")

    week_ago = days_ago(7)
    new = sorted((x for x in items if x["first_seen"] >= week_ago), key=lambda x: -x["score"])
    rising = sorted(items, key=lambda x: -x["gain7"])[:30]
    billing = summarize_ai_billing(repos)
    pricing = ((settings or {}).get("ai") or {}).get("pricing") or DEFAULT_PRICING
    updated_str = f"{datetime.now(BEIJING):%Y-%m-%d %H:%M}"

    kpis = "".join([
        _kpi_card("已收录项目", str(len(items)), f"共追踪 {len(repos)} 个仓库"),
        _kpi_card("7日新收录", str(len(new)), "点击查看近一周新晋项目", href="new.html"),
        _kpi_card("本周增速榜", f"Top {len(rising)}", "按 7 天 Star 增量排序", href="rising.html"),
        _kpi_card(
            "DeepSeek 累计花费",
            _cny(billing["cost_cny"]),
            f"{_k(billing['total_tokens'])} tokens · {billing['billed_count']} 次计费",
            href="usage.html",
            accent="is-cost",
        ),
    ])

    hero = (
        '<section class="radar-hero">'
        '<div class="radar-hero-main">'
        '<span class="radar-badge">每日自动更新 · 北京时间</span>'
        '<h1>GitHub 热门项目雷达</h1>'
        '<p class="radar-hero-desc">自动追踪 GitHub Trending 与高星新项目，多维评分过滤噪音，并使用 DeepSeek 生成中文简介与精细分类。</p>'
        f'<div class="radar-hero-meta">最后更新：<strong>{html.escape(updated_str)}（北京时间）</strong> · 已收录 <strong>{len(items)}</strong> / 追踪 <strong>{len(repos)}</strong> 个项目</div>'
        '</div>'
        '<div class="radar-hero-actions">'
        '<a class="radar-btn is-primary" href="rising.html">🔥 本周增速榜</a>'
        '<a class="radar-btn" href="new.html">✨ 7日新收录</a>'
        '<a class="radar-btn" href="usage.html">💰 Token 用量账单</a>'
        '</div>'
        '</section>'
    )

    billing_note = ""
    if billing["unbilled_count"] > 0:
        billing_note = f"\n> 另有 **{billing['unbilled_count']}** 个早期项目在接入统计前完成分类，[查看每日统计与单项目明细 →](usage.md)\n"
    else:
        billing_note = "\n[查看每日统计与单项目明细 →](usage.md)\n"

    index = [
        _nav("index"),
        "",
        hero,
        "",
        f'<div class="radar-stats-grid">{kpis}</div>',
        "",
        "## 分类浏览\n",
        f'<div class="radar-cat-grid">{"".join(cat_cards)}</div>',
        "",
        "## DeepSeek Token 用量与花费\n",
        _usage_overview_table(billing),
        billing_note,
    ]
    (DOCS_DIR / "index.md").write_text("\n".join(index), encoding="utf-8")

    new_page = [
        _nav("new"),
        "",
        '<header class="radar-page-head">'
        '<div class="radar-page-kicker"><a href="index.html">← 返回首页概览</a></div>'
        f'<h1>✨ 最近 7 天新收录（{len(new)}）</h1>'
        f'<p class="radar-page-desc">更新于 {html.escape(updated_str)}（北京时间） · 按综合评分由高到低排序，支持搜索、语言筛选与点击表头排序。</p>'
        '</header>',
        "",
        _table(new, True),
        "",
    ]
    (DOCS_DIR / "new.md").write_text("\n".join(new_page), encoding="utf-8")

    rising_page = [
        _nav("rising"),
        "",
        '<header class="radar-page-head">'
        '<div class="radar-page-kicker"><a href="index.html">← 返回首页概览</a></div>'
        f'<h1>🔥 本周增速榜 Top {len(rising)}</h1>'
        f'<p class="radar-page-desc">更新于 {html.escape(updated_str)}（北京时间） · 按最近 7 天 Star 增量排序，支持搜索、语言筛选与点击表头排序。</p>'
        '</header>',
        "",
        _table(rising, True),
        "",
    ]
    (DOCS_DIR / "rising.md").write_text("\n".join(rising_page), encoding="utf-8")

    (DOCS_DIR / "usage.md").write_text(_render_usage_page(billing, pricing, updated_str), encoding="utf-8")
    (DOCS_DIR / "data.json").write_text(
        json.dumps(sorted(items, key=lambda x: -x["score"]), ensure_ascii=False, indent=1), encoding="utf-8")
    (DOCS_DIR / "usage.json").write_text(
        json.dumps(billing, ensure_ascii=False, indent=1), encoding="utf-8")

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
    extra = (
        f"（另有 {billing['unbilled_count']} 个早期分类未记录接口 usage）"
        if billing["unbilled_count"] > 0 else ""
    )
    block = (
        f"{start}\n\n"
        f"**DeepSeek API 用量与计费**{extra} · [查看每日与单项目明细](docs/usage.md)\n\n"
        f"{_usage_overview_table(billing)}\n\n"
        f"**本周增速 Top 10**（{today()} 更新，共收录 {total} 个，[查看全部分类](docs/index.md)）\n\n"
        f"{_table(top, True)}\n\n"
        f"{end}"
    )
    text = re.sub(re.escape(start) + ".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    path.write_text(text, encoding="utf-8")


