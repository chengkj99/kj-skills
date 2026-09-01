#!/usr/bin/env python3
"""基于已刷新的 posts.json，下载并转写尚未有文字稿的视频号作品。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / ".codex/skills/kangjian-wechat-media/scripts"
sys.path.insert(0, str(ROOT))
from transcribe_shipinhao import (  # noqa: E402
    EXISTING_HINTS,
    TMP_DIR,
    TRANSCRIPT_DIR,
    download_media,
    existing_transcript_for,
    slug_from_title,
    transcribe,
    write_status,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--posts", type=Path, default=TMP_DIR / "posts.json")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--model", default="medium")
    parser.add_argument("--keep-media", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    posts = json.loads(args.posts.read_text(encoding="utf-8"))
    pending = []
    for post in posts:
        if existing_transcript_for(post["title"]):
            continue
        if not post.get("media_url"):
            continue
        pending.append(post)
        if args.limit and len(pending) >= args.limit:
            break

    results = []
    for index, post in enumerate(pending, start=1):
        slug = slug_from_title(post["title"])
        video_path = TMP_DIR / "media" / f"{slug}.mp4"
        raw_path = TMP_DIR / "raw" / f"{slug}-raw.md"
        print(f"[{index}/{len(pending)}] {post['title'][:40]}", flush=True)
        try:
            if not video_path.exists() or video_path.stat().st_size < 10_000:
                download_media(None, post["media_url"], video_path)
            transcribe(video_path, raw_path, args.model)
            post["status"] = "raw_ready"
            post["video_path"] = str(video_path)
            post["raw_path"] = str(raw_path)
            if not args.keep_media:
                video_path.unlink(missing_ok=True)
        except Exception as exc:  # noqa: BLE001
            post["status"] = "failed"
            post["error"] = str(exc)
            print(f"  failed: {exc}", flush=True)
        results.append(post)
        write_status(results)

    done = sum(1 for item in results if item.get("status") == "raw_ready")
    print(f"pending={len(pending)} done={done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
