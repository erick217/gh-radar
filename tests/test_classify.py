"""DeepSeek 返回校验、付费调用边界和失败处理的离线回归测试。"""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
import importlib
import io
import json
import os
import unittest
from unittest.mock import Mock, patch

import requests

from radar.classify import API_URL, InvalidClassification, classify, classify_one


CATEGORIES = ["开发工具/CLI工具", "其他/其他"]
FORMS = ["CLI工具", "其他"]
RESULT = {
    "summary": "管理开发任务的命令行工具", "category": CATEGORIES[0], "form": FORMS[0],
    "tags": ["开发工具", "命令行", "自动化"], "is_practical": True, "reason": "提供安装说明",
}
CFG = {"model": "deepseek-flash", "effort": "low", "readme_chars": 12000, "max_per_run": 2}


def response(content=None, finish="stop"):
    result = Mock()
    result.json.return_value = {
        "model": "deepseek-flash",
        "choices": [{"finish_reason": finish,
                     "message": {"content": json.dumps(RESULT) if content is None else content}}],
    }
    return result


def records():
    return {
        "demo/low": {"full_name": "demo/low", "score": {"total": 60}},
        "demo/high": {"full_name": "demo/high", "score": {"total": 90}},
        "demo/middle": {"full_name": "demo/middle", "score": {"total": 75}},
        "demo/cached": {"full_name": "demo/cached", "score": {"total": 100}, "ai": {"summary": "已缓存"}},
        "demo/excluded": {"full_name": "demo/excluded", "score": {"total": 100, "excluded": "fork"}},
    }


class ClassifierTests(unittest.TestCase):
    def test_valid_response_and_official_json_request(self):
        client = Mock()
        client.post.return_value = response()
        result = classify_one(client, {"full_name": "demo/tool"}, "README", CFG, CATEGORIES, FORMS)
        self.assertEqual(result["summary"], RESULT["summary"])
        self.assertEqual(result["provider"], "deepseek")
        self.assertEqual(result["model"], "deepseek-flash")
        self.assertIn("at", result)
        args, kwargs = client.post.call_args
        self.assertEqual(args[0], API_URL)
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["json"]["response_format"], {"type": "json_object"})
        self.assertIn(CATEGORIES[0], kwargs["json"]["messages"][0]["content"])

    def test_invalid_content_never_becomes_a_cached_classification(self):
        bad_results = [[], None, {}, dict(RESULT, category="未知/分类"),
                       dict(RESULT, form="未知形态"), dict(RESULT, is_practical="false"),
                       dict(RESULT, tags="不是数组"), dict(RESULT, tags=["只有一个"]),
                       dict(RESULT, tags=["标签", "标签", 42]), dict(RESULT, summary="字" * 41),
                       dict(RESULT, reason=""), dict(RESULT, unexpected="字段")]
        contents = ["", "not json"] + [json.dumps(item) for item in bad_results]
        for content in contents:
            with self.subTest(content=content):
                client = Mock()
                client.post.return_value = response(content)
                with self.assertRaises(ValueError):
                    classify_one(client, {"full_name": "demo/tool"}, "README", CFG, CATEGORIES, FORMS)

    def test_truncated_response_is_rejected(self):
        client = Mock()
        client.post.return_value = response(finish="length")
        with redirect_stdout(io.StringIO()):
            result = classify_one(client, {"full_name": "demo/tool"}, "README", CFG, CATEGORIES, FORMS)
        self.assertIsNone(result)

    def test_missing_or_empty_choices_are_rejected(self):
        for envelope in ({}, {"choices": []}, {"choices": [{}]}, None):
            with self.subTest(envelope=envelope):
                client = Mock()
                client.post.return_value.json.return_value = envelope
                with self.assertRaises(ValueError):
                    classify_one(client, {"full_name": "demo/tool"}, "README", CFG, CATEGORIES, FORMS)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key_does_not_create_a_session_or_read_readmes(self):
        gh = Mock()
        with patch("radar.classify.requests.Session") as session:
            stats = classify(records(), {"ai": CFG}, {}, CATEGORIES, FORMS, gh)
        self.assertTrue(stats["skipped_no_key"])
        session.assert_not_called()
        gh.readme.assert_not_called()

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-credential"}, clear=True)
    def test_limit_score_order_cached_and_excluded_records(self):
        repos = records()
        gh = Mock()
        with patch("radar.classify.requests.Session"), patch("radar.classify.classify_one") as one:
            one.side_effect = lambda *args: deepcopy(RESULT)
            stats = classify(repos, {"ai": CFG}, {"demo/high": "cached readme"}, CATEGORIES, FORMS, gh)
        self.assertEqual(stats["classified"], 2)
        self.assertEqual([call.args[1]["full_name"] for call in one.call_args_list],
                         ["demo/high", "demo/middle"])
        gh.readme.assert_called_once_with("demo/middle")
        self.assertNotIn("ai", repos["demo/low"])
        self.assertEqual(repos["demo/cached"]["ai"], {"summary": "已缓存"})

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-credential"}, clear=True)
    def test_auth_balance_and_rate_errors_stop_without_logging_response_secrets(self):
        for status in (401, 402, 429):
            with self.subTest(status=status):
                result = Mock(status_code=status)
                error = requests.HTTPError("private-response-body", response=result)
                output = io.StringIO()
                with patch("radar.classify.requests.Session"), \
                        patch("radar.classify.classify_one", side_effect=error) as one, \
                        redirect_stdout(output):
                    stats = classify(records(), {"ai": CFG}, {}, CATEGORIES, FORMS, Mock())
                self.assertEqual(stats["failed"], 1)
                self.assertEqual(one.call_count, 1)
                self.assertNotIn("private-response-body", output.getvalue())
                self.assertNotIn("test-credential", output.getvalue())

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-credential"}, clear=True)
    def test_bad_json_is_not_cached_and_does_not_block_next_record(self):
        repos = records()
        with patch("radar.classify.requests.Session"), \
                patch("radar.classify.classify_one", side_effect=[ValueError("invalid"), deepcopy(RESULT)]), \
                redirect_stdout(io.StringIO()):
            stats = classify(repos, {"ai": CFG}, {}, CATEGORIES, FORMS, Mock())
        self.assertEqual((stats["classified"], stats["failed"]), (1, 1))
        self.assertNotIn("ai", repos["demo/high"])
        self.assertIn("ai", repos["demo/middle"])

    def test_negative_cli_limit_fails_before_loading_or_writing_data(self):
        main = importlib.import_module("radar.__main__")
        with patch("sys.argv", ["radar", "--ai-limit", "-1"]), \
                patch.object(main, "load_settings") as load, redirect_stdout(io.StringIO()), \
                patch("sys.stderr", new_callable=io.StringIO), self.assertRaises(SystemExit) as result:
            main.main()
        self.assertEqual(result.exception.code, 2)
        load.assert_not_called()

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-credential"}, clear=True)
    def test_validation_diagnostic_contains_only_local_check_message(self):
        output = io.StringIO()
        with patch("radar.classify.requests.Session"), \
                patch("radar.classify.classify_one", side_effect=InvalidClassification("中文简介超过 40 字")), \
                redirect_stdout(output):
            stats = classify(records(), {"ai": dict(CFG, max_per_run=1)}, {}, CATEGORIES, FORMS, Mock())
        self.assertEqual(stats["failed"], 1)
        self.assertIn("中文简介超过 40 字", output.getvalue())
        self.assertNotIn("test-credential", output.getvalue())


if __name__ == "__main__":
    unittest.main()
