"""评分与过滤。所有分数都由已存数据算出，不调用任何外部服务。"""
from __future__ import annotations

import math
from datetime import date

from .store import days_ago, today


def _days_between(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def star_gain_7d(rec: dict) -> tuple[int, str]:
    """估算 7 天 star 增量，返回 (增量, 数据来源)。快照不足时依次退回到榜单数据、仓库年龄。"""
    stars = rec.get("stars") or {}
    if not stars:
        return 0, "none"
    now_day = max(stars)
    now = stars[now_day]

    older = [d for d in stars if d <= days_ago(7, now_day)]
    if older:
        return max(0, now - stars[max(older)]), "snapshot"

    first = min(stars)
    span = _days_between(first, now_day)
    if span >= 3:
        return max(0, round((now - stars[first]) * 7 / span)), "snapshot-partial"

    recent = [v for d, v in (rec.get("trending") or {}).items() if d >= days_ago(7, now_day)]
    weekly = max((v.get("weekly", 0) for v in recent), default=0)
    if weekly:
        return weekly, "trending-weekly"
    daily = max((v.get("daily", 0) for v in recent), default=0)
    if daily:
        return daily * 3, "trending-daily"  # 保守估计，避免单日暴涨被放大成一周

    age = max(1, _days_between(rec["created_at"], now_day))
    if age <= 60:
        return round(now * min(1, 7 / age)), "age"
    return 0, "none"


def _is_spike(rec: dict, gain7: int) -> bool:
    """近 7 天里单日增量占了 80% 以上，判为一日游/疑似刷星。"""
    stars = rec.get("stars") or {}
    days = sorted(d for d in stars if d >= days_ago(8, max(stars)))
    if len(days) < 4 or gain7 < 200:
        return False
    diffs = [stars[b] - stars[a] for a, b in zip(days, days[1:])]
    return max(diffs) > 0.8 * gain7


def score(rec: dict, settings: dict, override: dict) -> dict:
    cfg = settings["score"]
    flt = settings["filter"]
    now = today()

    # ---- 硬规则 ----
    excluded = None
    if rec.get("gone"):
        excluded = "仓库已不可访问"
    elif rec.get("fork"):
        excluded = "fork 项目"
    elif rec.get("archived"):
        excluded = "已归档"
    elif not rec.get("details_at"):
        excluded = "待补充详情"  # 上次运行被限流打断，下次会补抓
    elif rec.get("readme_chars", 0) < flt["min_readme_chars"]:
        excluded = "README 过短"

    text = f"{rec['full_name']} {rec.get('description', '')}".lower()
    is_resource = any(k.lower() in text for k in flt["resource_keywords"])

    # ---- 各项得分（0~1） ----
    gain7, gain_src = star_gain_7d(rec)
    velocity = min(1.0, math.log1p(gain7) / math.log1p(cfg["velocity_full"]))

    spike = _is_spike(rec, gain7)
    trending_days = sum(1 for d in (rec.get("trending") or {}) if d >= days_ago(30))
    history_days = len(rec.get("stars") or {})
    stability = 0.0 if spike else (1.0 if history_days >= 4 else 0.5)
    persistence = 0.7 * min(1.0, trending_days / 10) + 0.3 * stability

    pushed_age = _days_between(rec["pushed_at"], now)
    contributors = rec.get("contributors")
    health = (
        (0.4 if pushed_age <= 30 else 0.2 if pushed_age <= 90 else 0)
        + (0.3 if rec.get("latest_release") else 0)
        + (0.3 if (contributors or 0) >= 3 else 0.15 if contributors in (None, 2) else 0)
    )

    ai = rec.get("ai") or {}
    practical = (
        (0.4 if ai.get("is_practical") else 0.2 if not ai else 0)
        + (0.2 if rec.get("license") else 0)
        + (0.2 if rec.get("readme_chars", 0) >= 2000 else 0)
        + (0.2 if rec.get("install_hint") or rec.get("homepage") or is_resource else 0)
    )

    w = cfg["weights"]
    total = 100 * (w["velocity"] * velocity + w["persistence"] * persistence
                   + w["health"] * health + w["practical"] * practical)

    # ---- 软规则（降分） ----
    flags = []
    if spike:
        total -= 10
        flags.append("单日暴涨")
    if contributors == 1 and _days_between(rec["created_at"], now) < 7:
        total -= 15
        flags.append("新建且仅 1 名贡献者")

    total = round(max(0.0, total), 1)
    included = not override.get("hide") and (
        override.get("pin") or (excluded is None and total >= cfg["min_score"])
    )
    return {
        "total": total,
        "velocity": round(velocity, 2),
        "persistence": round(persistence, 2),
        "health": round(health, 2),
        "practical": round(practical, 2),
        "gain7": gain7,
        "gain7_source": gain_src,
        "trending_days_30": trending_days,
        "flags": flags,
        "is_resource": is_resource,
        "excluded": excluded,
        "included": bool(included),
    }
