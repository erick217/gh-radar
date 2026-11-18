"""页面渲染与简易每日 DeepSeek Usage 表格的离线测试。"""
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
    def test_summarize_ai_billing_groups_daily_totals(self):
        with patch.object(render_mod, "today", return_value="2026-11-14"):
            billing = summarize_ai_billing(_sample_repos())
        self.assertEqual(billing["classified_total"], 3)
        self.assertEqual(billing["billed_count"], 2)
        self.assertEqual(billing["unbilled_count"], 1)
        self.assertEqual(billing["total_tokens"], 4750)
        self.assertEqual(billing["cost_cny"], 0.01106)
        self.assertEqual(billing["today_billed"], 1)
        self.assertEqual(billing["today_cost_cny"], 0.00804)
        self.assertEqual(billing["daily"], [
            {"date": "2026-11-14", "total_tokens": 3500, "cost_cny": 0.00804},
            {"date": "2026-11-13", "total_tokens": 1250, "cost_cny": 0.00302},
        ])

    def test_render_writes_simple_daily_usage_table_and_landing_sections(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text(
                "# Title\n\n<!-- radar:start -->\nold\n<!-- radar:end -->\n",
                encoding="utf-8",
            )
            with patch.object(render_mod, "ROOT", root), \
                    patch.object(render_mod, "DOCS_DIR", docs), \
                    patch.object(render_mod, "today", return_value="2026-11-14"), \
                    patch.object(render_mod, "days_ago", return_value="2026-11-07"):
                summary = render(_sample_repos(), {})

            self.assertEqual(summary["included"], 3)
            self.assertEqual(summary["billed_repos"], 2)
            self.assertEqual(summary["total_tokens"], 4750)
            self.assertEqual(summary["cost_cny"], 0.01106)

            usage_md = (docs / "usage.md").read_text(encoding="utf-8")
            self.assertIn("nav_active: usage", usage_md)
            self.assertIn("| 日期 | 总 Tokens | 花费 (¥) |", usage_md)
            self.assertIn("| 2026-11-14 | 3,500 | ¥0.0080 |", usage_md)
            self.assertIn("| 2026-11-13 | 1,250 | ¥0.0030 |", usage_md)
            self.assertNotIn("单项目调用明细", usage_md)
            self.assertNotIn("计费单价参考", usage_md)

            usage_json = json.loads((docs / "usage.json").read_text(encoding="utf-8"))
            self.assertEqual(usage_json["cost_cny"], 0.01106)
            self.assertEqual(len(usage_json["daily"]), 2)

            index_md = (docs / "index.md").read_text(encoding="utf-8")
            self.assertIn("nav_active: index", index_md)
            self.assertIn('class="hero hero--collage"', index_md)
            self.assertIn('id="all-projects"', index_md)
            self.assertIn("全部收录项目（3）", index_md)
            self.assertIn('<a href="https://github.com/owner/alpha">owner/alpha</a>', index_md)
            self.assertIn('<a href="https://github.com/owner/beta">owner/beta</a>', index_md)
            self.assertIn('<a href="https://github.com/owner/legacy">owner/legacy</a>', index_md)
            self.assertIn('id="workflow"', index_md)
            self.assertIn("四维权重筛选准则", index_md)
            self.assertLess(index_md.index('id="all-projects"'), index_md.index('id="workflow"'))
            self.assertNotIn('id="features"', index_md)
            self.assertNotIn('id="statement"', index_md)
            self.assertNotIn('id="faq"', index_md)
            self.assertIn("<th>日期</th><th>总 Tokens</th><th>花费 (¥)</th>", index_md)
            self.assertIn("<td>2026-11-14</td><td>3,500</td><td>¥0.0080</td>", index_md)
            for line in index_md.splitlines():
                self.assertFalse(line.startswith("    "), f"4-space indented line would become code block: {line!r}")

            readme_md = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("**DeepSeek 每日 Usage**", readme_md)
            self.assertIn("| 日期 | 总 Tokens | 花费 (¥) |", readme_md)
            self.assertIn("| 2026-11-14 | 3,500 | ¥0.0080 |", readme_md)


if __name__ == "__main__":
    unittest.main()
