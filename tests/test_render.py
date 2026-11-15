"""页面渲染与 DeepSeek Usage 表格统计的离线测试。"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import radar.render as render_mod
from radar.render import render, summarize_ai_billing


def _sample_repos() -> dict[str, dict]:
    return {
        "owner/alpha": {
            "full_name": "owner/alpha",
            "url": "https://github.com/owner/alpha",
            "description": "alpha tool",
            "language": "Python",
            "stars": {"2026-11-14": 1500},
            "first_seen": "2026-11-14",
            "pushed_at": "2026-11-14",
            "score": {
                "total": 88.0,
                "gain7": 600,
                "flags": [],
                "is_resource": False,
                "included": True,
            },
            "ai": {
                "at": "2026-11-14",
                "model": "deepseek-flash",
                "summary": "Alpha 工具",
                "category": "AI/Agent",
                "form": "CLI工具",
                "tags": ["AI", "CLI", "Python"],
                "usage": {
                    "prompt_tokens": 3000,
                    "prompt_cache_hit_tokens": 1000,
                    "prompt_cache_miss_tokens": 2000,
                    "completion_tokens": 500,
                    "reasoning_tokens": 200,
                    "total_tokens": 3500,
                    "cost_cny": 0.00804,
                },
            },
        },
        "owner/beta": {
            "full_name": "owner/beta",
            "url": "https://github.com/owner/beta",
            "description": "beta tool",
            "language": "Rust",
            "stars": {"2026-11-13": 2000},
            "first_seen": "2026-11-13",
            "pushed_at": "2026-11-13",
            "score": {
                "total": 75.0,
                "gain7": 300,
                "flags": [],
                "is_resource": False,
                "included": True,
            },
            "ai": {
                "at": "2026-11-13",
                "model": "deepseek-flash",
                "summary": "Beta 工具",
                "category": "开发工具/CLI工具",
                "form": "CLI工具",
                "tags": ["Rust", "CLI", "Dev"],
                "usage": {
                    "prompt_tokens": 1000,
                    "prompt_cache_hit_tokens": 500,
                    "prompt_cache_miss_tokens": 500,
                    "completion_tokens": 250,
                    "reasoning_tokens": 100,
                    "total_tokens": 1250,
                    "cost_cny": 0.00302,
                },
            },
        },
        "owner/legacy": {
            "full_name": "owner/legacy",
            "url": "https://github.com/owner/legacy",
            "description": "legacy tool",
            "language": "Go",
            "stars": {"2026-11-10": 5000},
            "first_seen": "2026-11-10",
            "pushed_at": "2026-11-10",
            "score": {
                "total": 70.0,
                "gain7": 100,
                "flags": [],
                "is_resource": False,
                "included": True,
            },
            "ai": {
                "at": "2026-11-10",
                "model": "deepseek-flash",
                "summary": "早期已分类项目",
                "category": "后端/Web框架",
                "form": "库",
                "tags": ["Go", "Web", "API"],
            },
        },
    }


class RenderTests(unittest.TestCase):
    def test_summarize_ai_billing_groups_daily_and_records(self):
        with patch.object(render_mod, "today", return_value="2026-11-14"):
            billing = summarize_ai_billing(_sample_repos())
        self.assertEqual(billing["classified_total"], 3)
        self.assertEqual(billing["billed_count"], 2)
        self.assertEqual(billing["unbilled_count"], 1)
        self.assertEqual(billing["prompt_tokens"], 4000)
        self.assertEqual(billing["cache_hit_tokens"], 1500)
        self.assertEqual(billing["cache_miss_tokens"], 2500)
        self.assertEqual(billing["completion_tokens"], 750)
        self.assertEqual(billing["reasoning_tokens"], 300)
        self.assertEqual(billing["total_tokens"], 4750)
        self.assertEqual(billing["cost_cny"], 0.01106)
        self.assertEqual(billing["today_billed"], 1)
        self.assertEqual(billing["today_cost_cny"], 0.00804)
        self.assertEqual([d["date"] for d in billing["daily"]], ["2026-11-14", "2026-11-13"])
        self.assertEqual([r["full_name"] for r in billing["records"]], ["owner/alpha", "owner/beta"])

    def test_render_writes_usage_table_and_dashboard_pages(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text(
                "# Title\n\n<!-- radar:start -->\nold\n<!-- radar:end -->\n",
                encoding="utf-8",
            )
            settings = {"ai": {"pricing": {"input_cache_hit": 0.04, "input_cache_miss": 2.0, "output": 8.0}}}
            with patch.object(render_mod, "ROOT", root), \
                    patch.object(render_mod, "DOCS_DIR", docs), \
                    patch.object(render_mod, "today", return_value="2026-11-14"), \
                    patch.object(render_mod, "days_ago", return_value="2026-11-07"):
                summary = render(_sample_repos(), {}, settings)

            self.assertEqual(summary["included"], 3)
            self.assertEqual(summary["billed_repos"], 2)
            self.assertEqual(summary["total_tokens"], 4750)
            self.assertEqual(summary["cost_cny"], 0.01106)

            usage_md = (docs / "usage.md").read_text(encoding="utf-8")
            self.assertIn("| 周期 | 调用次数 | 输入 Tokens |", usage_md)
            self.assertIn("| 2026-11-14 | 1 | 3,000 | 1,000 | 33.3% | 2,000 | 500（含思维链 200） | 3,500 | ¥0.0080 |", usage_md)
            self.assertIn("[owner/alpha](https://github.com/owner/alpha)", usage_md)
            self.assertIn("| 输入（缓存命中） | ¥0.04 |", usage_md)

            usage_json = json.loads((docs / "usage.json").read_text(encoding="utf-8"))
            self.assertEqual(usage_json["cost_cny"], 0.01106)

            index_md = (docs / "index.md").read_text(encoding="utf-8")
            self.assertIn('class="radar-nav"', index_md)
            self.assertIn('class="radar-cat-grid"', index_md)
            self.assertIn("| 周期 | 调用次数 | 输入 Tokens |", index_md)

            readme_md = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("**DeepSeek API 用量与计费**", readme_md)
            self.assertIn("| 累计（已记录） | 2 | 4,000 | 1,500 | 37.5% | 2,500 | 750（含思维链 300） | 4,750 | ¥0.0111 |", readme_md)


if __name__ == "__main__":
    unittest.main()
