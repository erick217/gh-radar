"""采集候选项目，并刷新已追踪项目的 star 快照和元数据。"""
from __future__ import annotations

import hashlib
import re

from .github import GitHub, RateLimited
from .store import days_ago, delete_repo, today

INSTALL_HINT = re.compile(
    r"\b(pip|pipx|uv)\s+(tool\s+)?install\b|\bnpm\s+(i|install)\b|\bnpx\s|\bpnpm\s+(add|dlx)\b|\byarn\s+add\b"
    r"|\bbrew\s+install\b|\bcargo\s+install\b|\bgo\s+install\b|\bdocker\s+(run|compose|pull)\b"
    r"|\bwinget\s+install\b|\bscoop\s+install\b|\bapt(-get)?\s+install\b|\bcurl\s.+\|\s*(ba|z)?sh\b",
    re.IGNORECASE,
)

DETAILS_TTL_DAYS = 7


def _apply_meta(rec: dict, item: dict) -> None:
    rec.update(
        full_name=item["full_name"],
        url=item["html_url"],
        description=(item.get("description") or "").strip(),
        language=item.get("language"),
        topics=item.get("topics") or [],
        license=(item.get("license") or {}).get("spdx_id"),
        homepage=item.get("homepage") or None,
        created_at=item["created_at"][:10],
        pushed_at=item["pushed_at"][:10],
        archived=bool(item.get("archived")),
        fork=bool(item.get("fork")),
        forks=item.get("forks_count", 0),
    )
    rec.pop("gone", None)
    rec.setdefault("stars", {})[today()] = item["stargazers_count"]


def _refresh_details(gh: GitHub, rec: dict, readme_cache: dict[str, str]) -> None:
    name = rec["full_name"]
    readme = gh.readme(name)
    readme_cache[name] = readme
    rec["readme_chars"] = len(readme)
    rec["readme_hash"] = hashlib.sha1(readme.encode()).hexdigest()[:12]
    rec["install_hint"] = bool(INSTALL_HINT.search(readme))
    rec["latest_release"] = gh.latest_release(name)
    rec["contributors"] = gh.contributor_count(name)
    rec["details_at"] = today()


def collect(gh: GitHub, repos: dict[str, dict], settings: dict, readme_cache: dict[str, str]) -> dict:
    cfg = settings["collect"]
    now = today()
    seen: dict[str, dict] = {}  # 今天在榜单/搜索里出现的项目
    items: dict[str, dict] = {}  # 已拿到完整 API 数据的项目

    for period in cfg["trending_periods"]:
        for t in gh.trending(period):
            seen.setdefault(t["full_name"], {})[period] = t["gain"]

    q = f"created:>{days_ago(cfg['search_new_days'])} stars:>{cfg['search_new_min_stars']}"
    for item in gh.search_repos(q, cfg["search_new_limit"]):
        seen.setdefault(item["full_name"], {})
        items[item["full_name"]] = item

    # 需要刷新的已有项目：近期活跃的每天刷新，其余每周刷新一次
    active_since = days_ago(cfg["keep_tracking_days"])
    weekly_since = days_ago(7)
    todo = list(seen)
    for name, rec in repos.items():
        if name in seen or rec.get("gone"):
            continue
        last_snapshot = max(rec.get("stars") or {"": 0})
        if rec.get("last_seen", "") >= active_since or last_snapshot <= weekly_since:
            todo.append(name)

    stats = {"seen": len(seen), "refreshed": 0, "new": 0, "gone": 0, "rate_limited": False}
    try:
        for name in todo:
            item = items.get(name) or gh.repo(name)
            if item is None:
                if name in repos:
                    repos[name]["gone"] = True
                    stats["gone"] += 1
                continue

            canonical = item["full_name"]
            if canonical != name and name in repos:  # 仓库改名：迁移记录
                repos[canonical] = repos.pop(name)
                delete_repo(name)
            rec = repos.get(canonical)
            if rec is None:
                rec = repos[canonical] = {"first_seen": now, "trending": {}}
                stats["new"] += 1
            _apply_meta(rec, item)

            if name in seen:
                rec["last_seen"] = now
                if seen[name]:
                    rec.setdefault("trending", {})[now] = seen[name]
            if rec.get("details_at", "") <= days_ago(DETAILS_TTL_DAYS):
                _refresh_details(gh, rec, readme_cache)
            stats["refreshed"] += 1
    except RateLimited as e:
        print(f"[collect] {e}，本次只处理了一部分")
        stats["rate_limited"] = True
    return stats
