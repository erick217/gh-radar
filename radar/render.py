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

M_ARROW = (
    '<svg class="m-arrow" viewBox="0 0 12 12" aria-hidden="true">'
    '<path class="m-arrow__stem" d="M1 6h8"/>'
    '<path class="m-arrow__head" d="M4.5 2.5 8 6l-3.5 3.5"/>'
    '</svg>'
)

PHOSPHOR_ICONS = {
    "arrow_left": '<svg class="radar-icon" width="16" height="16" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M216 128H40M112 56L40 128L112 200" stroke="currentColor" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "check": '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="8.5" stroke="currentColor" stroke-width="1.5"/><path d="M6.5 10.2l2.3 2.3 4.7-4.8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "trend": '<svg class="radar-icon" width="24" height="24" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M232 56L136 152L96 112L24 184" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/><path d="M232 120V56H168" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "heart": '<svg class="radar-icon" width="24" height="24" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M32 128H76L104 64L144 192L176 128H224" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "clock": '<svg class="radar-icon" width="24" height="24" viewBox="0 0 256 256" fill="none" aria-hidden="true"><circle cx="128" cy="128" r="96" stroke="currentColor" stroke-width="18"/><path d="M128 72V128L168 152" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "wrench": '<svg class="radar-icon" width="24" height="24" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M104 128L40 192A18 18 0 0 0 65.5 217.5L129.5 153.5A56 56 0 0 0 202 74L168 108L148 88L182 54A56 56 0 0 0 104 128Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg>',
    "faq_book": '<svg class="radar-icon" width="28" height="28" viewBox="0 0 256 256" fill="none" aria-hidden="true"><circle cx="128" cy="128" r="96" stroke="currentColor" stroke-width="18"/><path d="M100 100A28 28 0 1 1 136 126.8C128 131.6 128 136 128 144" stroke="currentColor" stroke-width="18" stroke-linecap="round"/><circle cx="128" cy="180" r="10" fill="currentColor"/></svg>',
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
        f'<span class="radar-kpi-label">{html.escape(label)}</span>'
        f'<strong class="radar-kpi-value mono-num">{html.escape(value)}</strong>'
        f'<span class="radar-kpi-sub">{html.escape(sub)}</span>'
        f'</div>'
    )


def _category_pill(top: str, slug: str, count: int) -> str:
    icon = PHOSPHOR_ICONS[CAT_ICON_KEYS.get(top, "cube")]
    return (
        f'<div class="radar-cat-item">'
        f'<a class="radar-cat-row" href="categories/{slug}.html">{icon}<span>{html.escape(top)}</span></a>'
        f'<span class="radar-cat-row-count mono-num">{count}</span>'
        f'</div>'
    )


def _weight_visual_svg(kind: str) -> str:
    if kind == "velocity":
        bars = "".join(
            f'<rect x="{22 + i * 32}" y="{182 - h}" width="20" height="{h}" rx="5" fill="var(--accent)" fill-opacity="{0.35 + i * 0.1:.2f}"/>'
            for i, h in enumerate([34, 48, 62, 74, 96, 118, 144])
        )
        inner = (
            f'{bars}'
            '<line x1="16" y1="62" x2="244" y2="62" stroke="currentColor" stroke-opacity="0.28" stroke-dasharray="4 4" stroke-width="1.5"/>'
            '<text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">7D VELOCITY · CAP 80%</text>'
        )
    elif kind == "health":
        inner = (
            '<text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">HEALTH GATES</text>'
            '<text x="20" y="64" fill="currentColor" font-size="12" opacity="0.82">README &gt;= 200c</text>'
            '<rect x="20" y="74" width="220" height="14" rx="7" fill="currentColor" fill-opacity="0.08"/>'
            '<rect x="20" y="74" width="204" height="14" rx="7" fill="var(--accent)"/>'
            '<text x="20" y="116" fill="currentColor" font-size="12" opacity="0.82">License &amp; Docs</text>'
            '<rect x="20" y="126" width="220" height="14" rx="7" fill="currentColor" fill-opacity="0.08"/>'
            '<rect x="20" y="126" width="178" height="14" rx="7" fill="var(--accent)" fill-opacity="0.82"/>'
            '<text x="20" y="168" fill="currentColor" font-size="12" opacity="0.82">Contributors</text>'
            '<rect x="20" y="178" width="220" height="14" rx="7" fill="currentColor" fill-opacity="0.08"/>'
            '<rect x="20" y="178" width="146" height="14" rx="7" fill="var(--accent)" fill-opacity="0.65"/>'
        )
    elif kind == "continuity":
        pts = [(22, 174), (58, 162), (94, 146), (130, 128), (166, 98), (202, 78), (238, 50)]
        poly = " ".join(f"{x},{y}" for x, y in pts)
        area = f"22,190 {poly} 238,190"
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="var(--accent)"/>' for x, y in pts)
        inner = (
            '<text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">45D SNAPSHOT WINDOW</text>'
            f'<polygon points="{area}" fill="var(--accent)" fill-opacity="0.14"/>'
            f'<polyline points="{poly}" stroke="var(--accent)" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'{dots}'
            '<line x1="20" y1="190" x2="240" y2="190" stroke="currentColor" stroke-opacity="0.16" stroke-width="1.5"/>'
        )
    else:
        chips = [
            (20, 56, "CLI 工具"), (136, 56, "Agent"),
            (20, 108, "Web 应用"), (136, 108, "SDK / 库"),
        ]
        boxes = "".join(
            f'<rect x="{x}" y="{y}" width="104" height="38" rx="8" fill="currentColor" fill-opacity="0.06" stroke="currentColor" stroke-opacity="0.16"/>'
            f'<text x="{x + 52}" y="{y + 23}" text-anchor="middle" fill="currentColor" font-size="12" font-weight="500">{label}</text>'
            for x, y, label in chips
        )
        inner = (
            '<text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">PRACTICALITY SCORE &gt;= 55</text>'
            f'{boxes}'
            '<rect x="20" y="164" width="220" height="32" rx="8" fill="var(--accent)" fill-opacity="0.16"/>'
            '<text x="130" y="184" text-anchor="middle" fill="var(--accent)" font-size="12" font-weight="600">DeepSeek 中文功能摘要</text>'
        )
    return (
        f'<svg class="radar-weight-svg" viewBox="0 0 260 216" fill="none" role="img" aria-hidden="true">'
        f'{inner}'
        f'</svg>'
    )


def _category_chart_svg(cat_stats: list[tuple[str, int]], total: int) -> str:
    top_rows = sorted(cat_stats, key=lambda kv: (-kv[1], kv[0]))[:10]
    max_v = max((c for _, c in top_rows), default=1)
    bar_rows = []
    for idx, (name, count) in enumerate(top_rows):
        y = 48 + idx * 46
        bar_w = max(14, round(290 * (count / max_v)))
        pct = _pct(count, total)
        bar_rows.append(
            f'<text x="16" y="{y + 18}" fill="currentColor" font-size="13" font-weight="500">{html.escape(name)}</text>'
            f'<rect x="132" y="{y + 4}" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/>'
            f'<rect x="132" y="{y + 4}" width="{bar_w}" height="18" rx="9" fill="var(--accent)" fill-opacity="{0.92 - idx * 0.05:.2f}"/>'
            f'<text x="436" y="{y + 18}" fill="currentColor" font-size="12" font-family="var(--font-mono)">{count} ({pct})</text>'
        )
    return (
        '<svg class="radar-cat-svg" viewBox="0 0 540 520" fill="none" role="img" '
        'aria-label="各技术领域收录项目数量分布柱状图">'
        '<text x="16" y="24" fill="currentColor" font-size="13" font-weight="600" opacity="0.8">主要技术领域项目分布（Top 10）</text>'
        + "".join(bar_rows)
        + '</svg>'
    )


def _usage_chart_svg(daily: list[dict]) -> str:
    recent = list(reversed(daily[:7]))
    if not recent:
        return (
            '<svg class="radar-usage-svg" viewBox="0 0 520 176" fill="none" role="img" aria-label="每日 DeepSeek Token 消耗柱状图">'
            '<rect x="16" y="128" width="488" height="2" fill="currentColor" fill-opacity="0.16"/>'
            '<text x="16" y="88" fill="currentColor" font-size="12" opacity="0.65">暂无每日用量记录</text>'
            '</svg>'
        )
    max_tok = max((d["total_tokens"] for d in recent), default=1) or 1
    n = len(recent)
    slot_w = 488 / n
    bars = []
    for i, d in enumerate(recent):
        bw = min(44, max(18, round(slot_w * 0.56)))
        bx = round(16 + i * slot_w + (slot_w - bw) / 2, 1)
        bh = max(10, round(112 * (d["total_tokens"] / max_tok)))
        by = 132 - bh
        short_date = d["date"][-5:]
        bars.append(
            f'<rect x="{bx}" y="20" width="{bw}" height="112" rx="6" fill="currentColor" fill-opacity="0.06"/>'
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="var(--accent)"/>'
            f'<text x="{bx + bw / 2:.1f}" y="156" text-anchor="middle" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.72">{html.escape(short_date)}</text>'
        )
    return (
        '<svg class="radar-usage-svg" viewBox="0 0 520 176" fill="none" role="img" '
        'aria-label="近 7 日 DeepSeek Token 消耗趋势柱状图">'
        + "".join(bars)
        + '</svg>'
    )


def _hero_window_rows(rising: list[dict]) -> str:
    rows = []
    for it in rising[:5]:
        repo_name = it["full_name"].split("/")[-1]
        monogram = html.escape((repo_name[:2] if len(repo_name) >= 2 else repo_name).upper())
        lang = html.escape(it["language"] or "Repo")
        rows.append(
            f'<div class="d-row">'
            f'<span class="d-thumb" aria-hidden="true">{monogram}</span>'
            f'<div><b>{html.escape(it["full_name"])}</b><small>{lang} · ⭐ {_k(it["stars"])}</small></div>'
            f'<span class="num">+{_k(it["gain7"])}</span>'
            f'<span class="d-chip">{it["score"]:.0f} 分</span>'
            f'</div>'
        )
    if not rows:
        rows.append(
            '<div class="d-row">'
            '<span class="d-thumb" aria-hidden="true">GH</span>'
            '<div><b>等待首次同步</b><small>GitHub Actions · 就绪</small></div>'
            '<span class="num">+0</span>'
            '<span class="d-chip">就绪</span>'
            '</div>'
        )
    return "".join(rows)


def _render_index_page(
    items: list[dict],
    total_tracked: int,
    rising: list[dict],
    cat_pills: list[str],
    cat_stats: list[tuple[str, int]],
    billing: dict,
    updated_str: str,
) -> str:
    all_sorted = sorted(items, key=lambda x: (-x["score"], -x["gain7"]))

    hero_html = (
        '<section class="hero hero--collage" data-enter aria-labelledby="hero-h">\n'
        '  <div class="wrap">\n'
        '    <div class="hero-text grid hero__grid">\n'
        '      <div class="hero__text span-5">\n'
        f'        <p class="hero-notice">北京时间 <b>{html.escape(updated_str)}</b> 同步 · 今日 API 花费 <b>{_cny(billing["today_cost_cny"])}</b></p>\n'
        '        <h1 id="hero-h">GitHub 热门开源项目 每日筛选雷达</h1>\n'
        '        <p class="hero__lead">每日自动抓取 GitHub Trending 与高星新仓，通过四维权重模型剔除刷星与空壳仓库，再由 DeepSeek 生成中文简介与分类。</p>\n'
        '        <div class="btn-row">\n'
        f'          <a class="btn btn--primary" href="#all-projects">查看全部项目（{len(items)}）{M_ARROW}</a>\n'
        '          <a class="btn btn--secondary" href="rising.html">本周增速榜</a>\n'
        '        </div>\n'
        '        <dl class="hero-facts">\n'
        f'          <div><dt>已收录项目</dt><dd data-m-count>{len(items)}</dd></div>\n'
        f'          <div><dt>追踪仓库</dt><dd data-m-count>{total_tracked}</dd></div>\n'
        f'          <div><dt>累计 API 花费</dt><dd class="mono-num">{_cny(billing["cost_cny"])}</dd></div>\n'
        '        </dl>\n'
        '      </div>\n'
        '      <div class="hero__art span-6 start-7" role="img" aria-label="GitHub 热门项目雷达的增速榜界面与四维评分卡片">\n'
        '        <div class="ly-piece ly-piece--main d-win" aria-hidden="true">\n'
        '          <div class="d-win__bar"><span class="d-win__dots"><i></i><i></i><i></i></span><span>gh-radar · 本周增速快照</span></div>\n'
        '          <div class="d-win__body">\n'
        '            <div class="d-side">\n'
        '              <span><i></i>概览</span>\n'
        '              <span class="is-on"><i></i>全部项目</span>\n'
        '              <span><i></i>本周增速</span>\n'
        '              <span><i></i>7 日新仓</span>\n'
        '              <span class="d-side__label">热门分类</span>\n'
        '              <span><i></i>AI / Agent</span>\n'
        '              <span><i></i>开发工具</span>\n'
        '              <span><i></i>后端框架</span>\n'
        '            </div>\n'
        '            <div class="d-main">\n'
        f'              <div class="d-main__head"><h4>本周增速 Top 30</h4><span class="d-btn">共 {len(items)} 项</span></div>\n'
        f'              <div class="d-tabs"><span class="is-on">7日增量</span><span>综合评分 ≥55</span><span>高分 ≥85</span></div>\n'
        f'              <div class="d-rows">{_hero_window_rows(rising)}</div>\n'
        '            </div>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="ly-piece ly-piece--note d-card" aria-hidden="true" data-ly-steps="700">\n'
        '          <div class="d-card__row"><h5>四维准入校验</h5><span class="d-chip" data-step data-step-at="4">已收录</span></div>\n'
        '          <div class="d-note__line" data-step><i>✓</i><span><b>增速权重 35%</b> · 排除单日暴涨噪音</span></div>\n'
        '          <div class="d-note__line" data-step><i>✓</i><span><b>健康与活跃 45%</b> · 连续 45 天快照</span></div>\n'
        '          <div class="d-note__line" data-step><i>✓</i><span><b>DeepSeek Flash</b> · 单仓库仅分析一次</span></div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>'
    )

    all_projects_html = (
        '<section class="section ground-surface radar-section--auto" id="all-projects" aria-labelledby="all-projects-h" markdown="1">\n'
        '  <div class="wrap" markdown="1">\n'
        '    <div class="section-head section-head--split">\n'
        '      <div>\n'
        f'        <h2 id="all-projects-h">全部收录项目（{len(items)}）</h2>\n'
        '        <p>按四维综合评分由高到低排列，支持关键词搜索、按主分类或语言筛选，以及点击表头排序。</p>\n'
        '      </div>\n'
        '      <a class="link" href="new.html">查看 7 日新收录</a>\n'
        '    </div>\n\n'
        f'{_table(all_sorted, True)}\n\n'
        '  </div>\n'
        '</section>'
    )

    workflow_html = (
        '<section class="section ground-inverse" id="workflow" aria-labelledby="workflow-h" style="--hm: 2">\n'
        '  <div class="wrap">\n'
        '    <div class="section-head section-head--split">\n'
        '      <div>\n'
        '        <h2 id="workflow-h">四维权重筛选准则。<span class="muted">用近 45 天数据剔除短时刷星</span></h2>\n'
        '        <p>先排除 Fork、已归档与 README 过短的空壳仓库，再对近 45 天 Star 曲线与维护状态做定量评估，综合评分 ≥55 分方可入榜。</p>\n'
        '      </div>\n'
        '      <a class="link" href="rising.html">浏览本周增速榜</a>\n'
        '    </div>\n'
        '    <div class="radar-weight-grid">\n'
        '      <div class="radar-weight-card">\n'
        f'        <div class="radar-weight-top"><p class="t-stat">35%</p><h3>7 日 Star 增速</h3></div>\n'
        '        <p>计算最近 7 天真实增量，衡量社区短期关注度而非历史包袱。</p>\n'
        '        <div class="radar-weight-foot mono-num">单日增量 &gt;80% 直接扣 10 分</div>\n'
        f'        {_weight_visual_svg("velocity")}\n'
        '      </div>\n'
        '      <div class="radar-weight-card">\n'
        f'        <div class="radar-weight-top"><p class="t-stat">25%</p><h3>仓库健康度</h3></div>\n'
        '        <p>检查开源协议、文档篇幅与贡献者结构，过滤空壳项目。</p>\n'
        '        <div class="radar-weight-foot mono-num">建库 &lt;7 天且单人提交扣 15 分</div>\n'
        f'        {_weight_visual_svg("health")}\n'
        '      </div>\n'
        '      <div class="radar-weight-card">\n'
        f'        <div class="radar-weight-top"><p class="t-stat">20%</p><h3>持续演进力</h3></div>\n'
        '        <p>追踪连续 45 天历史快照变化与最近提交，剔除停更项目。</p>\n'
        '        <div class="radar-weight-foot mono-num">滚动保留 45 天增量快照序列</div>\n'
        f'        {_weight_visual_svg("continuity")}\n'
        '      </div>\n'
        '      <div class="radar-weight-card">\n'
        f'        <div class="radar-weight-top"><p class="t-stat">20%</p><h3>可运行实用性</h3></div>\n'
        '        <p>结合形态标签、安装命令与模型摘要，保留即开即用工具。</p>\n'
        '        <div class="radar-weight-foot mono-num">综合评分 ≥55 分方可入榜</div>\n'
        f'        {_weight_visual_svg("utility")}\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>'
    )

    cats_html = (
        '<section class="section ground-surface" id="categories" aria-labelledby="categories-h">\n'
        '  <div class="wrap">\n'
        '    <div class="grid grid--top">\n'
        '      <div class="span-5 radar-split-copy">\n'
        '        <h2 id="categories-h">12 个技术分类索引</h2>\n'
        f'        <p>当前共收录 {len(items)} 个开源项目，点击任意领域直接查看对应子分类与评分排名。</p>\n'
        f'        <div class="radar-cat-list">{"".join(cat_pills)}</div>\n'
        '      </div>\n'
        '      <div class="panel radar-cat-panel span-6 start-7">\n'
        f'        {_category_chart_svg(cat_stats, len(items))}\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>'
    )

    hit_rate = _pct(billing["cache_hit_tokens"], billing["prompt_tokens"])
    usage_html = (
        '<section class="section ground-base" id="usage" aria-labelledby="usage-h" markdown="1">\n'
        '  <div class="wrap" markdown="1">\n'
        '    <div class="grid grid--top" markdown="1">\n'
        '      <div class="span-5 radar-split-copy">\n'
        '        <h2 id="usage-h">DeepSeek 每日 Usage 与花费</h2>\n'
        '        <p>仅保留每日总 Tokens 与人民币花费，数据来源于模型接口实际返回值，历史结果永久缓存。</p>\n'
        '        <div class="radar-usage-mini">\n'
        f'          <div class="radar-usage-mini-item"><span>已计费分类</span><strong class="mono-num">{billing["billed_count"]} 次</strong></div>\n'
        f'          <div class="radar-usage-mini-item"><span>Prompt 缓存命中</span><strong class="mono-num">{hit_rate}</strong></div>\n'
        '        </div>\n'
        '        <div class="btn-row"><a class="btn btn--secondary btn--sm" href="usage.html">查看全部日期</a></div>\n'
        '      </div>\n'
        '      <div class="span-6 start-7 radar-usage-panel" markdown="1">\n'
        '        <div class="radar-usage-ledger ui ui-ledger" markdown="1">\n'
        f'          <div class="radar-usage-ledger-head"><span>近 7 日 DeepSeek 用量趋势</span><span class="mono-num">累计 {_cny(billing["cost_cny"])}</span></div>\n'
        f'          {_usage_chart_svg(billing["daily"])}\n'
        '          <div class="radar-table-wrap" markdown="1">\n\n'
        f'{_usage_daily_table(billing["daily"][:5])}\n\n'
        '          </div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>'
    )

    parts = [
        _front_matter(
            "概览",
            f"每日追踪 GitHub 热门实用开源项目，当前收录 {len(items)} 个项目，附四维筛选准则与 DeepSeek 每日用量统计。",
            nav_active="index",
        ),
        "",
        hero_html,
        "",
        all_projects_html,
        "",
        workflow_html,
        "",
        cats_html,
        "",
        usage_html,
        "",
    ]
    return "\n".join(parts)


def _render_usage_page(billing: dict, updated_str: str) -> str:
    hit_rate = _pct(billing["cache_hit_tokens"], billing["prompt_tokens"])
    kpis = "".join([
        _kpi_card("累计花费", _cny(billing["cost_cny"]), f"今日 {_cny(billing['today_cost_cny'])}", accent="is-cost"),
        _kpi_card("累计 Token", _k(billing["total_tokens"]), f"已记录 {billing['billed_count']} 次分类"),
        _kpi_card("缓存命中率", hit_rate, f"命中 {_k(billing['cache_hit_tokens'])} / 输入 {_k(billing['prompt_tokens'])}"),
        _kpi_card("已记录天数", str(len(billing["daily"])), "历史结果永久缓存不重复扣费"),
    ])
    parts = [
        _front_matter(
            "每日 Usage",
            "DeepSeek API 每日 Token 消耗与人民币花费简表。",
            nav_active="usage",
        ),
        "",
        '<section class="section">',
        '  <div class="wrap">',
        '    <div class="section-head" style="margin-bottom:var(--s-6)">',
        f'      <a class="radar-back-link" href="index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
        '      <h1>DeepSeek 每日 Usage 与花费</h1>',
        f'      <p>更新于 {html.escape(updated_str)}（北京时间） · 仅针对新增或未缓存项目调用 DeepSeek API，按实际返回总 Token 与单价每日汇总。</p>',
        '    </div>',
        f'    <div class="radar-stats-grid">{kpis}</div>',
        '  </div>',
        '</section>',
        "",
        '<h2 class="radar-sub-heading">每日用量统计</h2>',
        "",
        _usage_daily_table(billing["daily"]),
        "",
        f'<p class="radar-usage-summary">{html.escape(_usage_summary_text(billing))}</p>',
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
    cat_pills = []
    cat_stats = []
    for i, top in enumerate(order):
        slug = SLUGS.get(top, f"cat{i}")
        subs = by_top[top]
        count = sum(len(v) for v in subs.values())
        cat_pills.append(_category_pill(top, slug, count))
        cat_stats.append((top, count))
        parts = [
            _front_matter(
                top,
                f"{top}分类下的热门开源项目，共收录 {count} 个。",
            ),
            "",
            '<section class="section">',
            '  <div class="wrap">',
            '    <div class="section-head" style="margin-bottom:0">',
            f'      <a class="radar-back-link" href="../index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
            f'      <h1>{html.escape(top)}</h1>',
            f'      <p>共收录 {count} 个项目，各子分类按综合评分由高到低排列。</p>',
            '    </div>',
            '  </div>',
            '</section>',
            "",
        ]
        for sub, lst in sorted(subs.items(), key=lambda kv: -len(kv[1])):
            lst.sort(key=lambda x: -x["score"])
            parts.append(f'<h2 class="radar-sub-heading">{html.escape(sub)}（{len(lst)}）</h2>\n\n{_table(lst)}\n')
        (DOCS_DIR / "categories" / f"{slug}.md").write_text("\n".join(parts), encoding="utf-8")

    week_ago = days_ago(7)
    new = sorted((x for x in items if x["first_seen"] >= week_ago), key=lambda x: -x["score"])
    rising = sorted(items, key=lambda x: -x["gain7"])[:30]
    billing = summarize_ai_billing(repos)
    updated_str = f"{datetime.now(BEIJING):%Y-%m-%d %H:%M}"

    (DOCS_DIR / "index.md").write_text(
        _render_index_page(items, len(repos), rising, cat_pills, cat_stats, billing, updated_str),
        encoding="utf-8",
    )

    new_page = [
        _front_matter(
            "最近 7 天新收录",
            f"近 7 天新进入 GitHub 热门项目雷达的 {len(new)} 个开源项目。",
            nav_active="new",
        ),
        "",
        '<section class="section">',
        '  <div class="wrap">',
        '    <div class="section-head" style="margin-bottom:0">',
        f'      <a class="radar-back-link" href="index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
        f'      <h1>最近 7 天新收录（{len(new)}）</h1>',
        f'      <p>更新于 {html.escape(updated_str)}（北京时间） · 按综合评分由高到低排序，支持搜索、语言筛选与点击表头排序。</p>',
        '    </div>',
        '  </div>',
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
        '<section class="section">',
        '  <div class="wrap">',
        '    <div class="section-head" style="margin-bottom:0">',
        f'      <a class="radar-back-link" href="index.html">{PHOSPHOR_ICONS["arrow_left"]}<span>返回首页概览</span></a>',
        f'      <h1>本周增速榜 Top {len(rising)}</h1>',
        f'      <p>更新于 {html.escape(updated_str)}（北京时间） · 按最近 7 天 Star 增量排序，支持搜索、语言筛选与点击表头排序。</p>',
        '    </div>',
        '  </div>',
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
