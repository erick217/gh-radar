"""用 Claude 生成中文简介并归类。每个项目只处理一次，结果缓存在仓库记录的 ai 字段。"""
from __future__ import annotations

import json
import os

import anthropic

from .github import GitHub, RateLimited
from .store import today

# 支持服务端拒答回退（fallbacks）的模型
FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5"}

SYSTEM = """你是一名开源项目编辑，负责为 GitHub 热门项目建立中文索引。
根据给出的仓库信息和 README，输出：
- summary：一句话中文简介（40 字以内），说清楚它是什么、解决什么问题，不要营销腔。
- category：从给定清单中选最贴切的一个。纯教程、面试题、awesome 列表一律归入「学习资源」。
- form：项目形态，从给定清单中选。
- tags：3~5 个中文或英文关键词，便于搜索。
- is_practical：普通开发者或用户现在能否直接拿来用（有可安装/可运行的产物、文档足以上手）。纯 demo、论文代码、尚无可用版本的项目为 false。资源合集按内容质量判断。
- reason：一句话说明 is_practical 的判断依据。"""


def _schema(categories: list[str], forms: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "category": {"type": "string", "enum": categories},
            "form": {"type": "string", "enum": forms},
            "tags": {"type": "array", "items": {"type": "string"}},
            "is_practical": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["summary", "category", "form", "tags", "is_practical", "reason"],
        "additionalProperties": False,
    }


def _user_prompt(rec: dict, readme: str, limit: int) -> str:
    if len(readme) > limit:
        readme = readme[:limit] + "\n…（README 过长，已截断）"
    return (
        f"仓库：{rec['full_name']}\n"
        f"描述：{rec.get('description') or '（无）'}\n"
        f"主要语言：{rec.get('language') or '未知'}\n"
        f"Topics：{', '.join(rec.get('topics') or []) or '（无）'}\n"
        f"最新 Release：{rec.get('latest_release') or '无'}\n\n"
        f"<readme>\n{readme}\n</readme>"
    )


def classify_one(client: anthropic.Anthropic, rec: dict, readme: str, cfg: dict,
                 categories: list[str], forms: list[str]) -> dict | None:
    model = cfg["model"]
    kwargs = dict(
        model=model,
        max_tokens=4000,
        system=SYSTEM,
        messages=[{"role": "user", "content": _user_prompt(rec, readme, cfg["readme_chars"])}],
        output_config={"effort": cfg["effort"],
                       "format": {"type": "json_schema", "schema": _schema(categories, forms)}},
    )
    if model in FALLBACK_MODELS:
        resp = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
    else:
        resp = client.messages.create(**kwargs)

    if resp.stop_reason != "end_turn":
        print(f"[classify] {rec['full_name']} 未完成：stop_reason={resp.stop_reason}")
        return None
    text = next(b.text for b in resp.content if b.type == "text")
    data = json.loads(text)
    data["model"] = resp.model
    data["at"] = today()
    return data


def classify(repos: dict[str, dict], settings: dict, readme_cache: dict[str, str],
             categories: list[str], forms: list[str], gh: GitHub) -> dict:
    """对通过硬规则、还没分类的项目调用 Claude，按当前分数从高到低处理。"""
    stats = {"classified": 0, "failed": 0, "skipped_no_key": False}
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        stats["skipped_no_key"] = True
        return stats

    cfg = settings["ai"]
    todo = [r for r in repos.values()
            if not r.get("ai") and not (r.get("score") or {}).get("excluded")]
    todo.sort(key=lambda r: (r.get("score") or {}).get("total", 0), reverse=True)

    client = anthropic.Anthropic()
    for rec in todo[: cfg["max_per_run"]]:
        name = rec["full_name"]
        try:
            readme = readme_cache.get(name)
            if readme is None:
                readme = readme_cache[name] = gh.readme(name)
            result = classify_one(client, rec, readme, cfg, categories, forms)
        except RateLimited:
            break
        except anthropic.AuthenticationError:
            print("[classify] ANTHROPIC_API_KEY 无效，跳过 AI 分类")
            break
        except anthropic.RateLimitError:
            print("[classify] Claude API 限流，剩余项目留到下次")
            break
        except (anthropic.APIStatusError, anthropic.APIConnectionError, json.JSONDecodeError) as e:
            print(f"[classify] {name} 失败：{type(e).__name__}: {e}")
            result = None
        if result:
            rec["ai"] = result
            stats["classified"] += 1
        else:
            stats["failed"] += 1
    return stats
