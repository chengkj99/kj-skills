#!/usr/bin/env python3
"""从已登录的视频号助手会话下载自己的作品，并转成文字稿。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

WIKI_ROOT = Path("/Users/didi/ai_space/kj-llm-wiki")
CSV_PATH = (
    WIKI_ROOT
    / "raw/studio/funnel/published/shipinhao/runs/2026-08-16/exports/videos.csv"
)
TRANSCRIPT_DIR = WIKI_ROOT / "raw/studio/funnel/transcripts"
PROFILE_DIR = Path.home() / ".cache" / "kj-shipinhao-chrome"
TMP_DIR = Path("/tmp/shipinhao-transcription")
STT_ROOT = Path.home() / "work/stt"
STT_SCRIPT = Path.home() / ".codex/skills/kangjian-wechat-media/scripts/stt_local.py"
FINDER_USERNAME = "sphkaYvzi6N5lrd"
TZ = timezone(timedelta(hours=8))

FETCH_JS = """
async ({ pageSize, currentPage }) => {
  const urls = [
    '/micro/content/cgi-bin/mmfinderassistant-bin/post/post_list',
    '/cgi-bin/mmfinderassistant-bin/post/post_list',
  ];
  const body = {
    pageSize,
    currentPage,
    userpageType: 11,
    stickyOrder: false,
    timestamp: String(Date.now()),
    scene: 7,
    reqScene: 7,
  };
  const errors = [];
  for (const url of urls) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const text = await res.text();
      return { url, http: res.status, text };
    } catch (err) {
      errors.push(String(err));
    }
  }
  return { url: '', http: 0, text: '', errors };
}
"""

EXISTING_HINTS = {
    "文科生": "文科生不需要懂技术吗-文字稿.md",
    "食堂阿姨": "自从食堂阿姨刷到我的视频-文字稿.md",
    "提效不明显": "AI提效真相-文字稿.md",
    "AI编提效": "AI提效真相-文字稿.md",
    "5小时限额": "5小时的额度怎么使用-文字稿.md",
    "上下文不够用": "上下文不够用怎么办-文字稿.md",
    "阿里卸载": "阿里卸载claude后想和所有AI用户一个提醒-文字稿.md",
    "全栈学习方式": "全栈学习方式-文字稿.md",
    "星爷说人生就两个字": "星爷说人生就两个字-文字稿.md",
    "词元": "词元和token-文字稿.md",
    "精神内耗": "让我彻底戒掉精神内耗的二十个字-文字稿.md",
    "面对镜头不紧张": "口播时面对镜头不紧张-文字稿.md",
    "大话西游": "大话西游看500遍-文字稿.md",
    "每天都在用一个学习方法": "我每天都在用一个学习方法-文字稿.md",
    "账号被封之后": "两个Claude-Code账号被封之后-文字稿.md",
    "普通人一次翻身": "AI或许是我们普通人一次翻身的机会-文字稿.md",
    "真正吸引人的不是 AI": "会AI的人真正吸引人的不是AI-文字稿.md",
    "很多人以为": "很多人以为-文字稿.md",
    "上线没问题": "如何保证AI写的代码上线没问题-文字稿.md",
    "GPT5.6": "GPT5.6发布解析-文字稿.md",
    "再一次感谢": "再一次感谢每一个点开视频的家人朋友-文字稿.md",
    "650万的播放": "上一个视频已经有650万的播放-文字稿.md",
    "依然认为它属于第一梯队": "Claude-Code很强依然属于第一梯队-文字稿.md",
    "申请一个 Apple ID": "第一步登录Apple官网申请Apple-ID-文字稿.md",
    "我的账号今天也被封了": "我的账号今天也被封了-文字稿.md",
    "我们反而更忙了": "用了AI我们反而更忙了-文字稿.md",
    "没法替你建立工程思维": "AI没法替你建立工程思维-文字稿.md",
    "俞浩的75个视频": "看完俞浩的75个视频-文字稿.md",
    "AI Skill": "关于AI-Skill的3个真相-文字稿.md",
    "IP定位": "如何找到自己的IP定位-文字稿.md",
    "AI指挥官": "别忘了我们现在是AI指挥官-文字稿.md",
}


def one_line(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\n", " ")).strip()


def first_line(text: str) -> str:
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def format_time(ts: int | str) -> str:
    try:
        value = int(ts)
    except (TypeError, ValueError):
        return ""
    if value > 10_000_000_000:
        value //= 1000
    return datetime.fromtimestamp(value, TZ).strftime("%Y-%m-%d %H:%M:%S")


def share_url(export_id: str) -> str:
    if not export_id:
        return ""
    return (
        "https://channels.weixin.qq.com/web/pages/feed"
        f"?finderUsername={FINDER_USERNAME}&exportId={quote(export_id, safe='')}"
    )


def slug_from_title(title: str) -> str:
    text = re.sub(r"#[^\s#]+", "", title or "")
    text = re.sub(r"@\S+", "", text)
    text = re.sub(r"[\\/:*?\"<>|]", "", text)
    text = re.sub(r"\s+", "", text).strip("，。！？、：;,.!?-—_ ")
    if len(text) > 24:
        text = text[:24]
    return text or "未命名视频"


def parse_post(post: dict) -> dict:
    desc = post.get("desc") or {}
    description = desc.get("description") if isinstance(desc, dict) else ""
    media_list = desc.get("media") if isinstance(desc, dict) else []
    media = media_list[0] if media_list else {}
    export_id = post.get("exportId") or post.get("objectId") or ""
    title = first_line(description) or one_line(description)
    return {
        "title": title,
        "url": share_url(export_id),
        "feed_id": export_id,
        "publish_time": format_time(post.get("createTime") or 0),
        "media_url": media.get("url") or "",
        "duration": int(media.get("videoPlayLen") or 0),
        "file_size": int(media.get("fileSize") or 0),
        "description": description or "",
    }


def existing_transcript_for(title: str) -> Path | None:
    for hint, filename in EXISTING_HINTS.items():
        if hint in title:
            path = TRANSCRIPT_DIR / filename
            if path.exists():
                return path
    slug = slug_from_title(title)
    path = TRANSCRIPT_DIR / f"{slug}-文字稿.md"
    if path.exists():
        return path
    for file in TRANSCRIPT_DIR.glob("*-文字稿.md"):
        stem = file.name.replace("-文字稿.md", "")
        if stem and stem in title:
            return file
    return None


def fetch_posts(page, page_size: int = 20) -> list[dict]:
    posts: list[dict] = []
    seen: set[str] = set()
    current_page = 1
    declared_total = None
    while True:
        result = page.evaluate(FETCH_JS, {"pageSize": page_size, "currentPage": current_page})
        payload = json.loads(result["text"] or "{}")
        if payload.get("errCode") not in (0, None):
            raise RuntimeError(f"post_list 失败: {payload.get('errMsg') or payload}")
        data = payload.get("data") or {}
        if declared_total is None:
            declared_total = data.get("totalCount") or data.get("total")
        batch = data.get("list") or []
        if not batch:
            break
        for post in batch:
            item = parse_post(post)
            key = item["feed_id"] or item["title"]
            if key in seen:
                continue
            seen.add(key)
            posts.append(item)
        if declared_total and len(posts) >= int(declared_total):
            break
        if len(batch) < page_size:
            break
        current_page += 1
    return posts


def download_media(context, media_url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "curl",
        "-4",
        "-L",
        "--retry",
        "3",
        "--retry-delay",
        "2",
        "--max-time",
        "120",
        "-A",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H",
        "Referer: https://channels.weixin.qq.com/",
        "-o",
        str(dest),
        "-w",
        "%{http_code} %{size_download}",
        media_url,
    ]
    if context is not None:
        cookie_header = "; ".join(
            f"{cookie['name']}={cookie['value']}" for cookie in context.cookies()
        )
        if cookie_header:
            cmd[12:12] = ["-H", f"Cookie: {cookie_header}"]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0 or not dest.exists() or dest.stat().st_size < 10_000:
        raise RuntimeError(
            f"curl 下载失败 code={result.returncode} out={result.stdout.strip()} err={(result.stderr or '')[-200:]}"
        )


def transcribe(video_path: Path, raw_path: Path, model: str) -> None:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(STT_ROOT / "venv/bin/python"),
        str(STT_SCRIPT),
        "--input",
        str(video_path),
        "--output",
        str(raw_path),
        "--language",
        "zh",
        "--model-dir",
        str(STT_ROOT / "models/faster-whisper-medium"),
    ]
    subprocess.run(cmd, check=True)


def write_status(rows: list[dict]) -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    path = TMP_DIR / "status.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下载并转写自己的视频号作品")
    parser.add_argument("--limit", type=int, default=0, help="最多处理多少条未转写作品，0 表示全部")
    parser.add_argument("--model", default="medium")
    parser.add_argument("--keep-media", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--csv", type=Path, default=CSV_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        print("启动已登录的视频号助手 Chrome…", flush=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=args.headless,
            viewport={"width": 1440, "height": 960},
            locale="zh-CN",
            timeout=90_000,
            args=[
                "--hide-crash-restore-bubble",
                "--disable-session-crashed-bubble",
                "--disable-infobars",
            ],
        )
        print("Chrome 已启动", flush=True)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            print(f"打开助手后台: {page.url}", flush=True)
            page.goto(
                "https://channels.weixin.qq.com/platform/post/list",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            page.wait_for_timeout(2000)
            if "login" in page.url:
                print("需要重新扫码登录视频号助手。请在弹出的 Chrome 窗口里扫码。", flush=True)
                logged_in = False
                for _ in range(60):
                    page.wait_for_timeout(3000)
                    if "login" not in page.url and "channels.weixin.qq.com" in page.url:
                        logged_in = True
                        break
                if not logged_in:
                    raise RuntimeError("等待扫码超时，请重新运行脚本")
                page.goto(
                    "https://channels.weixin.qq.com/platform/post/list",
                    wait_until="domcontentloaded",
                    timeout=60_000,
                )
            print(f"已登录: {page.url}", flush=True)
            posts = fetch_posts(page)
            (TMP_DIR / "posts.json").write_text(
                json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            pending: list[dict] = []
            for post in posts:
                existing = existing_transcript_for(post["title"])
                if existing:
                    post["status"] = "skipped_existing"
                    post["transcript"] = str(existing)
                    continue
                if not post["media_url"]:
                    post["status"] = "no_media"
                    continue
                pending.append(post)

            if args.limit:
                pending = pending[: args.limit]

            results = []
            for index, post in enumerate(pending, start=1):
                slug = slug_from_title(post["title"])
                video_path = TMP_DIR / "media" / f"{slug}.mp4"
                raw_path = TMP_DIR / "raw" / f"{slug}-raw.md"
                print(f"[{index}/{len(pending)}] {post['title'][:40]}", flush=True)
                try:
                    download_media(context, post["media_url"], video_path)
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
        finally:
            context.close()

    print(f"posts={len(posts)} pending={len(pending)} done={sum(1 for x in results if x.get('status')=='raw_ready')}")
    print(f"status: {TMP_DIR / 'status.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
