#!/usr/bin/env python3
"""Normalize WeChat Official Account / Channels exports and generate archive reports."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


FIELD_ALIASES = {
    "id": ["id", "item_id", "article_id", "video_id", "content_id", "msgid", "biz_msg_id"],
    "parent_id": ["parent_id", "item_id", "article_id", "video_id", "content_id", "msgid", "biz_msg_id"],
    "title": ["title", "name", "desc", "description", "digest", "标题", "文章标题", "视频标题"],
    "url": ["url", "link", "article_url", "video_url", "source_url", "链接", "地址"],
    "publish_time": ["publish_time", "create_time", "created_at", "time", "date", "发布时间", "发表时间"],
    "read_count": ["read_count", "reads", "阅读", "阅读数"],
    "view_count": ["view_count", "play_count", "播放", "播放量", "观看"],
    "like_count": ["like_count", "liked_count", "likes", "点赞", "点赞数"],
    "comment_count": ["comment_count", "comments", "评论", "评论数", "留言数"],
    "share_count": ["share_count", "shares", "分享", "转发"],
    "favorite_count": ["favorite_count", "collect_count", "collected_count", "收藏"],
    "comment_id": ["comment_id", "reply_id", "留言id", "评论id"],
    "nickname": ["nickname", "user_name", "author", "comment_user", "昵称", "用户"],
    "content": ["content", "comment", "text", "message", "留言", "评论内容", "内容"],
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_markdown_table(path: Path) -> list[dict[str, Any]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines()]
    tables: list[dict[str, Any]] = []
    idx = 0
    while idx < len(lines) - 1:
        if lines[idx].startswith("|") and lines[idx + 1].startswith("|") and re.search(r"\|\s*:?-{3,}", lines[idx + 1]):
            headers = [cell.strip() for cell in lines[idx].strip("|").split("|")]
            idx += 2
            while idx < len(lines) and lines[idx].startswith("|"):
                cells = [cell.strip() for cell in lines[idx].strip("|").split("|")]
                if len(cells) == len(headers):
                    tables.append(dict(zip(headers, cells)))
                idx += 1
            continue
        idx += 1
    return tables


def load_rows(run_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".jsonl":
            rows.extend((path, row) for row in load_jsonl(path))
        elif path.suffix.lower() == ".csv":
            rows.extend((path, row) for row in load_csv(path))
        elif path.suffix.lower() == ".md":
            rows.extend((path, row) for row in load_markdown_table(path))
    return rows


def one_line(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def as_int(value: Any) -> int:
    if value is None:
        return 0
    text = one_line(value).replace(",", "")
    match = re.search(r"-?\d+", text)
    return int(match.group(0)) if match else 0


def field(row: dict[str, Any], key: str) -> Any:
    lowered = {str(k).strip().lower(): v for k, v in row.items()}
    raw = {str(k).strip(): v for k, v in row.items()}
    for alias in FIELD_ALIASES[key]:
        if alias in raw and raw[alias] not in (None, ""):
            return raw[alias]
        lower = alias.lower()
        if lower in lowered and lowered[lower] not in (None, ""):
            return lowered[lower]
    return ""


def stable_id(*parts: Any) -> str:
    seed = "|".join(one_line(part) for part in parts if one_line(part))
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


def is_comment(path: Path, row: dict[str, Any]) -> bool:
    name = path.name.lower()
    if re.search(r"comment|reply|留言|评论", name):
        return True
    return bool(field(row, "comment_id")) and bool(field(row, "content")) and not field(row, "title")


def normalize_work(path: Path, row: dict[str, Any], platform: str) -> dict[str, Any]:
    title = one_line(field(row, "title") or field(row, "content") or path.stem)
    url = one_line(field(row, "url"))
    publish_time = one_line(field(row, "publish_time"))
    item_id = one_line(field(row, "id")) or stable_id(platform, title, publish_time, url)
    return {
        "item_id": item_id,
        "platform": platform,
        "title": title,
        "url": url,
        "publish_time": publish_time,
        "read_count": as_int(field(row, "read_count")),
        "view_count": as_int(field(row, "view_count")),
        "like_count": as_int(field(row, "like_count")),
        "comment_count": as_int(field(row, "comment_count")),
        "share_count": as_int(field(row, "share_count")),
        "favorite_count": as_int(field(row, "favorite_count")),
        "source_file": str(path),
    }


def normalize_comment(path: Path, row: dict[str, Any], platform: str) -> dict[str, Any]:
    parent_id = one_line(field(row, "parent_id"))
    content = one_line(field(row, "content"))
    nickname = one_line(field(row, "nickname"))
    publish_time = one_line(field(row, "publish_time"))
    comment_id = one_line(field(row, "comment_id")) or stable_id(platform, parent_id, nickname, content, publish_time)
    return {
        "comment_id": comment_id,
        "item_id": parent_id,
        "platform": platform,
        "nickname": nickname,
        "content": content,
        "publish_time": publish_time,
        "like_count": as_int(field(row, "like_count")),
        "source_file": str(path),
    }


def classify_comment(text: str) -> str:
    if re.search(r"怎么|如何|为什么|能不能|教程|配置|报错|安装|token|模型|cursor|claude|codex|vibe", text, re.I):
        return "问题/教程需求"
    if re.search(r"不懂|区别|原理|架构|工程|逻辑|产品|上线|落地", text):
        return "概念/方法理解"
    if re.search(r"资料|课程|进群|案例|实战|源码|项目", text, re.I):
        return "资料/案例需求"
    if re.search(r"不同意|不对|质疑|但是|可是|没用|胡说", text):
        return "反对/质疑"
    if re.search(r"认同|有用|学到了|感谢|谢谢|真实|扎心|支持", text):
        return "共鸣/认可"
    return "普通反馈"


def load_manifest(path: Path, account: str, platform: str) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "account": account,
        "platform": platform,
        "items": {},
        "comment_ids_by_item": {},
        "runs": [],
    }


def update_manifest(manifest: dict[str, Any], items: list[dict[str, Any]], comments: list[dict[str, Any]], run_id: str, full_refresh: bool) -> dict[str, Any]:
    item_map = manifest.setdefault("items", {})
    previous_ids = set(item_map)
    new_items: list[str] = []
    changed_items: list[str] = []
    for item in items:
        item_id = item["item_id"]
        old = item_map.get(item_id)
        if old is None:
            new_items.append(item_id)
        elif any(as_int(old.get(k)) != as_int(item.get(k)) for k in ["read_count", "view_count", "like_count", "comment_count", "share_count", "favorite_count"]):
            changed_items.append(item_id)
        item_map[item_id] = item

    comments_by_item = manifest.setdefault("comment_ids_by_item", {})
    new_comments = 0
    for comment in comments:
        comment_id = comment["comment_id"]
        item_id = comment.get("item_id") or "__unknown__"
        known = set(comments_by_item.get(item_id, []))
        if comment_id not in known:
            new_comments += 1
            known.add(comment_id)
        comments_by_item[item_id] = sorted(known)

    run_record = {
        "run_id": run_id,
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "full_refresh": full_refresh,
        "items_in_run": len(items),
        "comments_in_run": len(comments),
        "new_items": len(set(new_items)),
        "new_comments": new_comments,
        "changed_items": len(set(changed_items)),
    }
    manifest.setdefault("runs", []).append(run_record)
    manifest["last_run"] = run_record
    manifest["total_items"] = len(item_map)
    manifest["total_known_comments"] = sum(len(ids) for ids in comments_by_item.values())
    manifest["new_item_ids_last_run"] = sorted(set(new_items))
    manifest["changed_item_ids_last_run"] = sorted(set(changed_items) - (set(new_items) - previous_ids))
    return manifest


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: one_line(item.get("publish_time")), reverse=True)


def build_full_ledger(account: str, platform: str, items: list[dict[str, Any]], comments: list[dict[str, Any]], date: str, run_id: str) -> str:
    comments_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for comment in comments:
        comments_by_item[comment.get("item_id") or "__unknown__"].append(comment)

    item_label = "公众号文章" if platform == "wechat" else "视频号作品"
    lines = [
        f"# {item_label}完整流水账：{account}",
        "",
        "## 采集信息",
        f"- 账号：{account}",
        f"- 平台：{platform}",
        f"- 采集日期：{date}",
        f"- Run：{run_id}",
        f"- 内容数：{len(items)}",
        f"- 评论/留言数：{len(comments)}",
        "",
        "## 内容索引",
        "| 序号 | 发布时间 | ID | 标题 | 阅读/播放 | 点赞 | 评论 | 收藏 | 分享 | 链接 |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, item in enumerate(sort_items(items), 1):
        views = item["read_count"] or item["view_count"]
        title = one_line(item["title"]).replace("|", "\\|")
        url = item.get("url") or ""
        link = f"[打开]({url})" if url else ""
        lines.append(f"| {idx} | {item['publish_time']} | `{item['item_id']}` | {title} | {views} | {item['like_count']} | {item['comment_count']} | {item['favorite_count']} | {item['share_count']} | {link} |")

    lines.extend(["", "## 评论/留言流水"])
    for idx, item in enumerate(sort_items(items), 1):
        item_comments = sorted(comments_by_item.get(item["item_id"], []), key=lambda c: c["like_count"], reverse=True)
        lines.extend(["", f"### {idx}. {one_line(item['title'])}", "", f"- ID：`{item['item_id']}`", f"- 本次评论/留言数：{len(item_comments)}", ""])
        if not item_comments:
            lines.append("_本次未导入评论/留言。_")
            continue
        lines.extend(["| 序号 | 时间 | 点赞 | 昵称 | 内容 |", "|---:|---|---:|---|---|"])
        for cidx, comment in enumerate(item_comments, 1):
            content = one_line(comment["content"]).replace("|", "\\|")
            nickname = one_line(comment["nickname"]).replace("|", "\\|")
            lines.append(f"| {cidx} | {comment['publish_time']} | {comment['like_count']} | {nickname} | {content} |")
    return "\n".join(lines)


def build_analysis(account: str, platform: str, items: list[dict[str, Any]], comments: list[dict[str, Any]], date: str) -> str:
    def score(item: dict[str, Any]) -> int:
        return (item["read_count"] or item["view_count"]) + item["like_count"] * 5 + item["comment_count"] * 8 + item["favorite_count"] * 6 + item["share_count"] * 6

    top_items = sorted(items, key=score, reverse=True)[:20]
    label_counter = Counter(classify_comment(comment["content"]) for comment in comments)
    top_comments = sorted(comments, key=lambda comment: comment["like_count"], reverse=True)[:50]
    item_label = "公众号文章" if platform == "wechat" else "视频号作品"

    lines = [
        f"# {item_label}复盘分析：{account}",
        "",
        "## 采集信息",
        f"- 账号：{account}",
        f"- 平台：{platform}",
        f"- 采集日期：{date}",
        f"- 内容数：{len(items)}",
        f"- 评论/留言数：{len(comments)}",
        "- 分析性质：基于导出数据的初步复盘；如导出字段不全，需要结合后台截图或手工补充",
        "",
        "## 数据概览",
        f"- 总阅读/播放：{sum(item['read_count'] or item['view_count'] for item in items)}",
        f"- 总点赞：{sum(item['like_count'] for item in items)}",
        f"- 总评论/留言：{sum(item['comment_count'] for item in items)}",
        f"- 总收藏：{sum(item['favorite_count'] for item in items)}",
        f"- 总分享：{sum(item['share_count'] for item in items)}",
        "",
        "## 高互动内容 Top 20",
        "| 排名 | 发布时间 | 标题 | 阅读/播放 | 点赞 | 评论 | 收藏 | 分享 | 复盘提示 |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, item in enumerate(top_items, 1):
        title = one_line(item["title"]).replace("|", "\\|")
        link_title = f"[{title}]({item['url']})" if item.get("url") else title
        lines.append(f"| {idx} | {item['publish_time']} | {link_title} | {item['read_count'] or item['view_count']} | {item['like_count']} | {item['comment_count']} | {item['favorite_count']} | {item['share_count']} | 对照标题、开头、转化入口和评论问题 |")

    lines.extend(["", "## 评论/留言类型分布", "| 类型 | 数量 | 用途 |", "|---|---:|---|"])
    usage = {
        "问题/教程需求": "转为教程、排错清单或下一篇",
        "概念/方法理解": "补概念解释、方法论或案例",
        "资料/案例需求": "转为资料包入口、案例篇或社群 FAQ",
        "反对/质疑": "转为澄清篇、边界篇或反例篇",
        "共鸣/认可": "沉淀为标题和开头素材",
        "普通反馈": "观察整体语气和选题接受度",
    }
    for label, count in label_counter.most_common():
        lines.append(f"| {label} | {count} | {usage.get(label, '待人工判断')} |")

    lines.extend(["", "## 高价值评论/留言候选", "| 序号 | 内容 ID | 点赞 | 类型 | 内容 |", "|---:|---|---:|---|---|"])
    for idx, comment in enumerate(top_comments, 1):
        content = one_line(comment["content"]).replace("|", "\\|")
        lines.append(f"| {idx} | `{comment.get('item_id') or '__unknown__'}` | {comment['like_count']} | {classify_comment(comment['content'])} | {content} |")

    lines.extend([
        "",
        "## 下一步建议",
        "- 把高互动内容和抖音高互动主题做交叉验证，找出可跨平台复用的表达。",
        "- 对评论/留言中的问题类反馈生成教程型选题，对质疑类反馈生成边界澄清型选题。",
        "- 更新后继续运行 `$content-growth-review`，把平台数据转成内容调整和选题池。",
    ])
    return "\n".join(lines)


def build_latest_summary(account: str, platform: str, manifest: dict[str, Any], date: str) -> str:
    items = sort_items(list(manifest.get("items", {}).values()))
    last_run = manifest.get("last_run", {})
    lines = [
        f"# {platform} 媒体数据 latest 摘要：{account}",
        "",
        f"- 更新时间：{date}",
        f"- 已知内容数：{len(items)}",
        f"- 已知评论/留言 ID 数：{manifest.get('total_known_comments', 0)}",
        f"- 最近 run：{last_run.get('run_id', '')}",
        f"- 最近新增内容：{last_run.get('new_items', 0)}",
        f"- 最近新增评论/留言：{last_run.get('new_comments', 0)}",
        "",
        "## 最新内容",
        "| 序号 | 发布时间 | 标题 | 阅读/播放 | 点赞 | 评论 | 收藏 | 分享 | 链接 |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, item in enumerate(items[:30], 1):
        title = one_line(item["title"]).replace("|", "\\|")
        link = f"[打开]({item['url']})" if item.get("url") else ""
        lines.append(f"| {idx} | {item['publish_time']} | {title} | {item['read_count'] or item['view_count']} | {item['like_count']} | {item['comment_count']} | {item['favorite_count']} | {item['share_count']} | {link} |")
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--platform", required=True, choices=["wechat", "shipinhao"])
    parser.add_argument("--account", required=True)
    parser.add_argument("--full-refresh", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = load_rows(args.run_dir)
    if not rows:
        raise SystemExit(f"no supported export rows found under {args.run_dir}")

    items: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    seen_items: set[str] = set()
    seen_comments: set[str] = set()
    for path, row in rows:
        if is_comment(path, row):
            comment = normalize_comment(path, row, args.platform)
            if comment["comment_id"] not in seen_comments and comment["content"]:
                comments.append(comment)
                seen_comments.add(comment["comment_id"])
        else:
            item = normalize_work(path, row, args.platform)
            if item["item_id"] not in seen_items:
                items.append(item)
                seen_items.add(item["item_id"])

    manifest_path = args.archive_dir / "manifest" / f"{args.account}-manifest.json"
    manifest = load_manifest(manifest_path, args.account, args.platform)
    manifest = update_manifest(manifest, items, comments, args.run_dir.name, args.full_refresh)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    full_path = args.archive_dir / f"{args.date}-{args.account}-{args.platform}-full-ledger.md"
    analysis_path = args.archive_dir / f"{args.date}-{args.account}-{args.platform}-review-analysis.md"
    latest_path = args.archive_dir / f"latest-{args.account}-summary.md"
    write_text(full_path, build_full_ledger(args.account, args.platform, items, comments, args.date, args.run_dir.name))
    write_text(analysis_path, build_analysis(args.account, args.platform, items, comments, args.date))
    write_text(latest_path, build_latest_summary(args.account, args.platform, manifest, args.date))

    print(json.dumps({
        "items": len(items),
        "comments": len(comments),
        "manifest_total_items": manifest.get("total_items", 0),
        "manifest_total_known_comments": manifest.get("total_known_comments", 0),
        "new_items": manifest.get("last_run", {}).get("new_items", 0),
        "new_comments": manifest.get("last_run", {}).get("new_comments", 0),
        "full_ledger": str(full_path),
        "review_analysis": str(analysis_path),
        "latest_summary": str(latest_path),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
