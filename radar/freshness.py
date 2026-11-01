"""定时补偿检查与成功发布标记，只依赖标准库，可在安装依赖之前运行。"""
from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BEIJING = ZoneInfo("Asia/Shanghai")
MARKER = Path(__file__).resolve().parent.parent / "data" / "last-publish.json"


def needs_refresh(event: str, marker: dict, now: datetime) -> tuple[bool, str]:
    local = now.astimezone(BEIJING)
    if event != "schedule":
        return True, "手动运行，立即更新"
    if local.hour < 9:
        return False, "北京时间尚未到 09:00，等待当天更新窗口"
    if marker.get("data_date") == local.date().isoformat():
        return False, "今天已成功发布，跳过重复采集与模型调用"
    return True, "今天尚未成功发布，执行更新或补偿"


def load_marker(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def record_publish(path: Path, data_date: str, run_id: str, now: datetime) -> None:
    date.fromisoformat(data_date)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "data_date": data_date,
        "published_at": now.astimezone(BEIJING).isoformat(timespec="seconds"),
        "run_id": run_id,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mark-published", action="store_true")
    parser.add_argument("--data-date")
    args = parser.parse_args()
    now = datetime.now(BEIJING)
    if args.mark_published:
        if not args.data_date:
            parser.error("--mark-published 需要 --data-date")
        record_publish(MARKER, args.data_date, os.environ.get("GITHUB_RUN_ID", ""), now)
        print(f"已记录成功发布的数据日期：{args.data_date}")
        return
    refresh, reason = needs_refresh(os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch"),
                                    load_marker(MARKER), now)
    print(reason)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"refresh={str(refresh).lower()}\ndata_date={now.date().isoformat()}\n")


if __name__ == "__main__":
    main()
