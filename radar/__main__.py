"""每日运行入口：python -m radar [--no-ai] [--no-collect]"""
from __future__ import annotations

import argparse

from .classify import classify
from .collect import collect
from .github import GitHub
from .render import render
from .score import score
from .store import (days_ago, delete_repo, load_overrides, load_repos, load_settings,
                    load_taxonomy, save_repo)


def _score_all(repos: dict, settings: dict, overrides: dict) -> None:
    for name, rec in repos.items():
        if rec.get("stars"):
            rec["score"] = score(rec, settings, overrides.get(name) or {})


def _prune(repos: dict, overrides: dict) -> int:
    """删除长期不活跃、从未被收录的噪音记录，避免数据无限增长。"""
    removed = 0
    for name in list(repos):
        rec = repos[name]
        stale = rec.get("last_seen", "") < days_ago(90)
        if name not in overrides and stale and not (rec.get("score") or {}).get("included"):
            delete_repo(name)
            del repos[name]
            removed += 1
    return removed


def main() -> None:
    ap = argparse.ArgumentParser(description="GitHub 热门项目雷达")
    ap.add_argument("--no-ai", action="store_true", help="跳过 AI 分类")
    ap.add_argument("--no-collect", action="store_true", help="跳过采集；AI 分类仍可能读取 GitHub README")
    ap.add_argument("--ai-limit", type=int, help="本次最多分类多少个项目，覆盖配置值")
    args = ap.parse_args()
    if args.ai_limit is not None and args.ai_limit < 0:
        ap.error("--ai-limit 不能小于 0")

    settings = load_settings()
    if args.ai_limit is not None:
        settings["ai"]["max_per_run"] = args.ai_limit
    overrides = load_overrides()
    categories, forms = load_taxonomy()
    repos = load_repos()
    gh = GitHub()
    readme_cache: dict[str, str] = {}

    if not args.no_collect:
        print("[collect]", collect(gh, repos, settings, readme_cache))
    _score_all(repos, settings, overrides)
    if not args.no_ai:
        print("[classify]", classify(repos, settings, readme_cache, categories, forms, gh))
        _score_all(repos, settings, overrides)  # AI 的 is_practical 会影响实用分

    print("[prune] 删除", _prune(repos, overrides), "条过期记录")
    for rec in repos.values():
        save_repo(rec)
    print("[render]", render(repos, overrides), f"GitHub API 调用 {gh.calls} 次")


if __name__ == "__main__":
    main()
