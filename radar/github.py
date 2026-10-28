"""GitHub 访问：Trending 页面抓取 + REST API。"""
from __future__ import annotations

import os
import re
import time

import requests
from bs4 import BeautifulSoup

API = "https://api.github.com"


class RateLimited(Exception):
    pass


class GitHub:
    def __init__(self, token: str | None = None):
        self.s = requests.Session()
        self.s.headers["Accept"] = "application/vnd.github+json"
        self.s.headers["User-Agent"] = "gh-radar"
        token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"
        self.calls = 0

    def _get(self, url: str, params: dict | None = None, accept: str | None = None) -> requests.Response:
        headers = {"Accept": accept} if accept else None
        for attempt in range(3):
            self.calls += 1
            r = self.s.get(url, params=params, headers=headers, timeout=30)
            if r.status_code in (403, 429) and r.headers.get("x-ratelimit-remaining") == "0":
                raise RateLimited(f"GitHub API 配额用完，重置时间 {r.headers.get('x-ratelimit-reset')}")
            if r.status_code in (403, 429) and "secondary rate limit" in r.text.lower():
                time.sleep(int(r.headers.get("retry-after", "30")))
                continue
            if r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            return r
        return r

    # ---------- Trending ----------
    def trending(self, since: str) -> list[dict]:
        """返回 [{"full_name", "gain"}]，gain 是该周期内新增 star。页面改版时返回空列表。"""
        r = self.s.get("https://github.com/trending", params={"since": since}, timeout=30)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        out = []
        for row in soup.select("article.Box-row"):
            a = row.select_one("h2 a")
            if not a or not a.get("href"):
                continue
            full_name = a["href"].strip("/")
            if full_name.count("/") != 1:
                continue
            gain = 0
            m = re.search(r"([\d,]+)\s+stars?\s+(today|this week|this month)", row.get_text(" ", strip=True))
            if m:
                gain = int(m.group(1).replace(",", ""))
            out.append({"full_name": full_name, "gain": gain})
        return out

    # ---------- REST ----------
    def search_repos(self, query: str, limit: int) -> list[dict]:
        r = self._get(f"{API}/search/repositories",
                      {"q": query, "sort": "stars", "order": "desc", "per_page": min(limit, 100)})
        r.raise_for_status()
        return r.json().get("items", [])[:limit]

    def repo(self, full_name: str) -> dict | None:
        """仓库不存在（删除、改为私有）时返回 None。改名会被 GitHub 自动重定向。"""
        r = self._get(f"{API}/repos/{full_name}")
        if r.status_code in (404, 451):
            return None
        r.raise_for_status()
        return r.json()

    def readme(self, full_name: str) -> str:
        r = self._get(f"{API}/repos/{full_name}/readme", accept="application/vnd.github.raw")
        return r.text if r.status_code == 200 else ""

    def latest_release(self, full_name: str) -> str | None:
        r = self._get(f"{API}/repos/{full_name}/releases", {"per_page": 1})
        if r.status_code == 200 and r.json():
            return r.json()[0].get("tag_name")
        return None

    def contributor_count(self, full_name: str) -> int | None:
        """超大仓库 GitHub 不返回贡献者列表，此时返回 None。"""
        r = self._get(f"{API}/repos/{full_name}/contributors", {"per_page": 1, "anon": "true"})
        if r.status_code != 200:
            return None
        m = re.search(r'page=(\d+)>; rel="last"', r.headers.get("link", ""))
        return int(m.group(1)) if m else len(r.json())
