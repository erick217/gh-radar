"""配置与数据读写。每个仓库一个 JSON 文件，放在 data/repos/ 下，git 历史就是完整的变更记录。"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "repos"
DOCS_DIR = ROOT / "docs"


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def days_ago(n: int, ref: str | None = None) -> str:
    base = date.fromisoformat(ref or today())
    return (base - timedelta(days=n)).isoformat()


def load_yaml(rel: str) -> dict:
    path = ROOT / rel
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_settings() -> dict:
    return load_yaml("config/settings.yaml")


def load_taxonomy() -> tuple[list[str], list[str]]:
    """返回 (["AI/Agent", ...], ["库", ...])。"""
    tax = load_yaml("config/taxonomy.yaml")
    cats = [f"{top}/{sub}" for top, subs in tax["categories"].items() for sub in subs]
    return cats, list(tax["forms"])


def load_overrides() -> dict:
    return load_yaml("overrides.yaml")


def _path(full_name: str) -> Path:
    return DATA_DIR / (full_name.replace("/", "__") + ".json")


def load_repos() -> dict[str, dict]:
    repos = {}
    for p in sorted(DATA_DIR.glob("*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        repos[rec["full_name"]] = rec
    return repos


def save_repo(rec: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _path(rec["full_name"]).write_text(text, encoding="utf-8")


def delete_repo(full_name: str) -> None:
    _path(full_name).unlink(missing_ok=True)
