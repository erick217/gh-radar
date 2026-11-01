"""验证补偿调度不会因跨时区或重复触发而重复使用模型。"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from radar.freshness import BEIJING, load_marker, needs_refresh, record_publish


class FreshnessTests(unittest.TestCase):
    def test_today_success_skips_scheduled_refresh(self):
        now = datetime(2026, 11, 1, 10, tzinfo=BEIJING)
        refresh, _ = needs_refresh("schedule", {"data_date": "2026-11-01"}, now)
        self.assertFalse(refresh)

    def test_yesterday_or_missing_marker_requires_refresh(self):
        now = datetime(2026, 11, 1, 10, tzinfo=BEIJING)
        for marker in ({}, {"data_date": "2026-10-31"}, {"data_date": "invalid"}):
            with self.subTest(marker=marker):
                self.assertTrue(needs_refresh("schedule", marker, now)[0])

    def test_manual_refresh_still_runs_after_today_success(self):
        now = datetime(2026, 11, 1, 10, tzinfo=BEIJING)
        self.assertTrue(needs_refresh("workflow_dispatch", {"data_date": "2026-11-01"}, now)[0])

    def test_late_run_from_previous_day_waits_until_morning(self):
        now = datetime(2026, 11, 1, 8, 59, tzinfo=BEIJING)
        self.assertFalse(needs_refresh("schedule", {}, now)[0])

    def test_day_boundary_uses_beijing_time(self):
        now = datetime(2026, 10, 31, 23, tzinfo=timezone.utc)
        self.assertFalse(needs_refresh("schedule", {"data_date": "2026-10-31"}, now)[0])
        now = datetime(2026, 11, 1, 1, 17, tzinfo=timezone.utc)
        self.assertTrue(needs_refresh("schedule", {"data_date": "2026-10-31"}, now)[0])

    def test_marker_records_data_day_even_when_deployment_crosses_midnight(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "last-publish.json"
            now = datetime(2026, 11, 2, 0, 5, tzinfo=BEIJING)
            record_publish(path, "2026-11-01", "123", now)
            marker = load_marker(path)
            self.assertEqual(marker["data_date"], "2026-11-01")
            self.assertEqual(marker["run_id"], "123")
            self.assertTrue(needs_refresh("schedule", marker, now.replace(hour=9))[0])

    def test_bad_marker_does_not_disable_updates(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "last-publish.json"
            self.assertEqual(load_marker(path), {})
            for contents in ("not-json", "[]", "null"):
                path.write_text(contents, encoding="utf-8")
                self.assertEqual(load_marker(path), {})


if __name__ == "__main__":
    unittest.main()
