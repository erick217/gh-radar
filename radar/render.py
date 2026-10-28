"""把收录的项目生成 Markdown 页面（docs/ 目录，可直接用 GitHub Pages 发布）。"""
from __future__ import annotations

import json
import re
from collections import defaultdict

from .store import DOCS_DIR, ROOT, days_ago, today

SLUGS = {
    "AI": "ai", "开发工具": "devtools", "前端": "frontend", "后端": "backend", "数据": "data",
    "运维与云原生": "ops", "安全": "security", "效率与自托管": "productivity", "多媒体": "media",
    "移动与桌面": "apps", "学习资源": "learning", "其他": "other", "未分类": "unclassified",
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


def render(repos: dict[str, dict], overrides: dict) -> dict:
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
    toc = []
    for i, top in enumerate(order):
        slug = SLUGS.get(top, f"cat{i}")
        subs = by_top[top]
        count = sum(len(v) for v in subs.values())
        toc.append(f"- [{top}](categories/{slug}.md)（{count}）："
                   + "、".join(f"{s} {len(v)}" for s, v in sorted(subs.items())))
        parts = [f"# {top}\n", f"[← 返回目录](../index.md) · 共 {count} 个项目，按分数排序\n"]
        for sub, lst in sorted(subs.items(), key=lambda kv: -len(kv[1])):
            lst.sort(key=lambda x: -x["score"])
            parts.append(f"## {sub}（{len(lst)}）\n\n{_table(lst)}\n")
        (DOCS_DIR / "categories" / f"{slug}.md").write_text("\n".join(parts), encoding="utf-8")

    week_ago = days_ago(7)
    new = sorted((x for x in items if x["first_seen"] >= week_ago), key=lambda x: -x["score"])
    rising = sorted(items, key=lambda x: -x["gain7"])[:30]

    index = [
        "# GitHub 热门项目雷达\n",
        f"更新于 {today()} · 已收录 {len(items)} 个项目 · 共追踪 {len(repos)} 个\n",
        "- [最近 7 天新收录](new.md)",
        "- [本周增速榜](rising.md)\n",
        "## 分类\n", *toc, "",
    ]
    (DOCS_DIR / "index.md").write_text("\n".join(index), encoding="utf-8")
    (DOCS_DIR / "new.md").write_text(
        f"# 最近 7 天新收录（{len(new)}）\n\n[← 返回目录](index.md)\n\n{_table(new, True)}\n", encoding="utf-8")
    (DOCS_DIR / "rising.md").write_text(
        f"# 本周增速榜 Top {len(rising)}\n\n[← 返回目录](index.md)\n\n{_table(rising, True)}\n", encoding="utf-8")
    (DOCS_DIR / "data.json").write_text(
        json.dumps(sorted(items, key=lambda x: -x["score"]), ensure_ascii=False, indent=1), encoding="utf-8")

    _update_readme(rising[:10], len(items))
    return {"included": len(items), "new_7d": len(new)}


def _update_readme(top: list[dict], total: int) -> None:
    path = ROOT / "README.md"
    start, end = "<!-- radar:start -->", "<!-- radar:end -->"
    text = path.read_text(encoding="utf-8")
    block = (f"{start}\n\n**本周增速 Top 10**（{today()} 更新，共收录 {total} 个，"
             f"[查看全部分类](docs/index.md)）\n\n{_table(top, True)}\n\n{end}")
    text = re.sub(re.escape(start) + ".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    path.write_text(text, encoding="utf-8")
