#!/usr/bin/env python3
"""Incrementally merge MediaCrawler Douyin JSONL and generate Markdown reports."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ACCOUNT = "kangjian-douyin"
SOURCE_URL = "https://www.douyin.com/user/MS4wLjABAAAAU0QYHCmBaS2uUvbuc5XfY-XTJJCybRun-GHf2kpR6o0?from_tab_name=main"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def as_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def fmt_time(ts: Any) -> str:
    n = as_int(ts)
    if not n:
        return ""
    return dt.datetime.fromtimestamp(n).strftime("%Y-%m-%d %H:%M:%S")


def one_line(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def slugify(text: str, max_len: int = 72) -> str:
    text = one_line(text)
    text = re.sub(r"[\\/:*?\"<>|#`]+", "-", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:max_len].strip("-") or "untitled")


def find_jsonl(run_dir: Path, kind: str) -> Path | None:
    candidates = sorted(run_dir.glob(f"**/{kind}_*.jsonl"))
    return candidates[-1] if candidates else None


def video_url(work: dict[str, Any]) -> str:
    return str(work.get("aweme_url") or f"https://www.douyin.com/video/{work.get('aweme_id', '')}")


def transcript_path(work: dict[str, Any]) -> str:
    title = one_line(work.get("title") or work.get("desc") or str(work.get("aweme_id", "")))
    return f"raw/studio/funnel/transcripts/{slugify(title)}-文字稿.md"


def classify_comment(text: str) -> list[str]:
    labels: list[str] = []
    if re.search(r"怎么|如何|为啥|为什么|哪里|哪儿|能不能|可以吗|求|教程|配置|登录|报错|安装|额度|token|模型|cursor|claude|codex|windsurf|trae|copilot|qoder|glm", text, re.I):
        labels.append("工具/配置问题")
    if re.search(r"不懂|什么意思|区别|原理|架构|概念|逻辑|本质|边界|替代|提效|工程", text):
        labels.append("概念理解")
    if re.search(r"案例|实战|演示|项目|demo|源码|课程|进群|资料", text, re.I):
        labels.append("案例/教程需求")
    if re.search(r"不对|不同意|反驳|扯|胡说|没用|垃圾|降智|质疑|但是|可是|问题是", text):
        labels.append("反对/质疑")
    if re.search(r"说得对|太对|认同|有用|学到了|感谢|谢谢|共鸣|真实|扎心|支持|赞", text):
        labels.append("共鸣/认可")
    return labels or ["普通反馈"]


def sort_works(works: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(works, key=lambda item: as_int(item.get("create_time")), reverse=True)


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "account": ACCOUNT,
            "source_url": SOURCE_URL,
            "works": {},
            "comment_ids_by_aweme": {},
            "runs": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def update_manifest(
    manifest: dict[str, Any],
    works: list[dict[str, Any]],
    comments: list[dict[str, Any]],
    run_id: str,
    full_refresh: bool,
) -> dict[str, Any]:
    previous_ids = set(manifest.get("works", {}).keys())
    new_ids: list[str] = []
    changed_ids: list[str] = []

    works_by_id = manifest.setdefault("works", {})
    for work in works:
        aweme_id = str(work.get("aweme_id") or "")
        if not aweme_id:
            continue
        old = works_by_id.get(aweme_id)
        if old is None:
            new_ids.append(aweme_id)
            works_by_id[aweme_id] = work
            continue
        metric_keys = ["liked_count", "comment_count", "collected_count", "share_count"]
        if any(as_int(old.get(key)) != as_int(work.get(key)) for key in metric_keys):
            changed_ids.append(aweme_id)
        if as_int(work.get("last_modify_ts")) >= as_int(old.get("last_modify_ts")):
            works_by_id[aweme_id] = work

    comment_ids_by_aweme = manifest.setdefault("comment_ids_by_aweme", {})
    new_comment_count = 0
    for comment in comments:
        aweme_id = str(comment.get("aweme_id") or "")
        comment_id = str(comment.get("comment_id") or "")
        if not aweme_id or not comment_id:
            continue
        ids = set(comment_ids_by_aweme.get(aweme_id, []))
        if comment_id not in ids:
            new_comment_count += 1
            ids.add(comment_id)
        comment_ids_by_aweme[aweme_id] = sorted(ids)

    run_record = {
        "run_id": run_id,
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "full_refresh": full_refresh,
        "works_in_run": len({str(w.get("aweme_id")) for w in works if w.get("aweme_id")}),
        "comments_in_run": len(comments),
        "new_works": len(new_ids),
        "new_comments": new_comment_count,
        "changed_works": len(set(changed_ids)),
    }
    manifest.setdefault("runs", []).append(run_record)
    manifest["last_run"] = run_record
    manifest["total_works"] = len(works_by_id)
    manifest["total_known_comments"] = sum(len(v) for v in comment_ids_by_aweme.values())
    manifest["new_work_ids_last_run"] = sorted(set(new_ids))
    manifest["changed_work_ids_last_run"] = sorted(set(changed_ids) - (set(new_ids) - previous_ids))
    return manifest


def build_full_ledger(works: list[dict[str, Any]], comments: list[dict[str, Any]], date: str, run_label: str) -> str:
    comments_by_aweme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for comment in comments:
        comments_by_aweme[str(comment.get("aweme_id") or "")].append(comment)

    lines: list[str] = [
        f"# 抖音已发布作品完整流水账：{ACCOUNT}",
        "",
        "## 采集信息",
        f"- 账号：{ACCOUNT}",
        f"- 主页：{SOURCE_URL}",
        f"- 采集日期：{date}",
        f"- Run：{run_label}",
        f"- 作品数：{len(works)}",
        f"- 一级评论数：{len(comments)}",
        "- 二级评论：未抓取",
        "- 视频文件/文字稿：未在本次 MediaCrawler 流程生成；文字稿后续由 local-stt-transcription 生成",
        "",
        "## 作品索引",
        "| 序号 | 发布时间 | 作品 ID | 标题 | 点赞 | 评论 | 收藏 | 分享 | 链接 | 文字稿路径 |",
        "|---:|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for idx, work in enumerate(sort_works(works), 1):
        aweme_id = str(work.get("aweme_id") or "")
        title = one_line(work.get("title") or work.get("desc") or aweme_id).replace("|", "\\|")
        lines.append(
            f"| {idx} | {fmt_time(work.get('create_time'))} | {aweme_id} | {title} | "
            f"{as_int(work.get('liked_count'))} | {as_int(work.get('comment_count'))} | "
            f"{as_int(work.get('collected_count'))} | {as_int(work.get('share_count'))} | "
            f"[打开]({video_url(work)}) | `{transcript_path(work)}` |"
        )

    lines.extend(["", "## 评论流水"])
    for idx, work in enumerate(sort_works(works), 1):
        aweme_id = str(work.get("aweme_id") or "")
        title = one_line(work.get("title") or work.get("desc") or aweme_id)
        lines.extend(["", f"### {idx}. {title}", "", f"- 作品 ID：`{aweme_id}`", f"- 链接：{video_url(work)}", f"- 本次抓取评论数：{len(comments_by_aweme.get(aweme_id, []))}", ""])
        work_comments = sorted(comments_by_aweme.get(aweme_id, []), key=lambda c: as_int(c.get("like_count")), reverse=True)
        if not work_comments:
            lines.append("_本次未抓到一级评论。_")
            continue
        lines.extend(["| 序号 | 时间 | 点赞 | 昵称 | 评论 |", "|---:|---|---:|---|---|"])
        for cidx, comment in enumerate(work_comments, 1):
            content = one_line(comment.get("content")).replace("|", "\\|")
            nickname = one_line(comment.get("nickname")).replace("|", "\\|")
            lines.append(f"| {cidx} | {fmt_time(comment.get('create_time'))} | {as_int(comment.get('like_count'))} | {nickname} | {content} |")
    return "\n".join(lines)


def build_analysis(works: list[dict[str, Any]], comments: list[dict[str, Any]], date: str) -> str:
    comments_by_aweme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for comment in comments:
        comments_by_aweme[str(comment.get("aweme_id") or "")].append(comment)

    top_engagement = sorted(
        works,
        key=lambda w: as_int(w.get("liked_count")) + as_int(w.get("comment_count")) * 2 + as_int(w.get("collected_count")) + as_int(w.get("share_count")),
        reverse=True,
    )[:20]
    top_comment = sorted(works, key=lambda w: as_int(w.get("comment_count")), reverse=True)[:20]

    label_counter: Counter[str] = Counter()
    comment_rows: list[tuple[int, str, list[str], str]] = []
    for comment in comments:
        content = one_line(comment.get("content"))
        labels = classify_comment(content)
        label_counter.update(["、".join(labels)])
        comment_rows.append((as_int(comment.get("like_count")), str(comment.get("aweme_id") or ""), labels, content))
    top_comments = sorted(comment_rows, reverse=True)[:50]

    lines: list[str] = [
        f"# 抖音已发布作品复盘分析：{ACCOUNT}",
        "",
        "## 采集信息",
        f"- 账号：{ACCOUNT}",
        f"- 主页：{SOURCE_URL}",
        f"- 采集日期：{date}",
        f"- 作品数：{len(works)}",
        f"- 一级评论数：{len(comments)}",
        "- 分析性质：基于作品数据与一级评论的初步内容复盘；未纳入视频文字稿语义",
        "",
        "## 数据概览",
        f"- 总点赞：{sum(as_int(w.get('liked_count')) for w in works)}",
        f"- 总评论：{sum(as_int(w.get('comment_count')) for w in works)}",
        f"- 总收藏：{sum(as_int(w.get('collected_count')) for w in works)}",
        f"- 总分享：{sum(as_int(w.get('share_count')) for w in works)}",
        "",
        "## 高互动作品 Top 20",
        "| 排名 | 发布时间 | 标题 | 点赞 | 评论 | 收藏 | 分享 | 复盘提示 |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for idx, work in enumerate(top_engagement, 1):
        title = one_line(work.get("title") or work.get("desc") or work.get("aweme_id")).replace("|", "\\|")
        lines.append(
            f"| {idx} | {fmt_time(work.get('create_time'))} | [{title}]({video_url(work)}) | "
            f"{as_int(work.get('liked_count'))} | {as_int(work.get('comment_count'))} | "
            f"{as_int(work.get('collected_count'))} | {as_int(work.get('share_count'))} | 值得补文字稿并拆解钩子/结构 |"
        )

    lines.extend(["", "## 评论驱动作品 Top 20", "| 排名 | 发布时间 | 标题 | 平台评论数 | 本次抓取评论数 | 复盘提示 |", "|---:|---|---|---:|---:|---|"])
    for idx, work in enumerate(top_comment, 1):
        aweme_id = str(work.get("aweme_id") or "")
        title = one_line(work.get("title") or work.get("desc") or aweme_id).replace("|", "\\|")
        lines.append(f"| {idx} | {fmt_time(work.get('create_time'))} | [{title}]({video_url(work)}) | {as_int(work.get('comment_count'))} | {len(comments_by_aweme.get(aweme_id, []))} | 优先看问题意识和争议点 |")

    lines.extend(["", "## 评论类型分布", "| 类型 | 数量 | 用途 |", "|---|---:|---|"])
    usage = {
        "工具/配置问题": "转成教程、排错清单或下一集",
        "概念理解": "补概念解释、方法论页或类比案例",
        "案例/教程需求": "转成实战演示、案例篇",
        "反对/质疑": "转成澄清篇、反例篇或边界说明",
        "共鸣/认可": "沉淀为选题验证和标题素材",
        "普通反馈": "作为整体情绪和语气参考",
    }
    for label, count in label_counter.most_common():
        lines.append(f"| {label} | {count} | {usage.get(label, '待人工判断')} |")

    lines.extend(["", "## 高价值评论候选", "| 序号 | 作品 ID | 点赞 | 类型 | 评论 |", "|---:|---|---:|---|---|"])
    for idx, (likes, aweme_id, labels, content) in enumerate(top_comments, 1):
        escaped_content = content.replace("|", "\\|")
        lines.append(f"| {idx} | `{aweme_id}` | {likes} | {'、'.join(labels)} | {escaped_content} |")

    lines.extend([
        "",
        "## 下一步建议",
        "- 优先给高互动作品补齐文字稿，组合分析“标题/开头/论证/评论反馈”。",
        "- 把工具问题类评论沉淀成教程选题，把反对/质疑类评论沉淀成澄清篇或边界篇。",
        "- 对新增作品单独观察 24 小时与 7 天两次数据，避免只看发布当天波动。",
    ])
    return "\n".join(lines)


def build_latest_summary(manifest: dict[str, Any], date: str) -> str:
    works = sort_works(list(manifest.get("works", {}).values()))
    last_run = manifest.get("last_run", {})
    lines = [
        f"# 抖音媒体数据 latest 摘要：{ACCOUNT}",
        "",
        f"- 更新时间：{date}",
        f"- 账号主页：{SOURCE_URL}",
        f"- 已知作品数：{len(works)}",
        f"- 已知一级评论 ID 数：{manifest.get('total_known_comments', 0)}",
        f"- 最近 run：{last_run.get('run_id', '')}",
        f"- 最近新增作品：{last_run.get('new_works', 0)}",
        f"- 最近新增评论：{last_run.get('new_comments', 0)}",
        "",
        "## 最新作品",
        "| 序号 | 发布时间 | 标题 | 点赞 | 评论 | 收藏 | 分享 | 链接 |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for idx, work in enumerate(works[:30], 1):
        title = one_line(work.get("title") or work.get("desc") or work.get("aweme_id")).replace("|", "\\|")
        lines.append(
            f"| {idx} | {fmt_time(work.get('create_time'))} | {title} | "
            f"{as_int(work.get('liked_count'))} | {as_int(work.get('comment_count'))} | "
            f"{as_int(work.get('collected_count'))} | {as_int(work.get('share_count'))} | [打开]({video_url(work)}) |"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--account", default=ACCOUNT)
    parser.add_argument("--full-refresh", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contents_path = find_jsonl(args.run_dir, "creator_contents")
    comments_path = find_jsonl(args.run_dir, "creator_comments")
    if contents_path is None:
        raise SystemExit(f"creator_contents_*.jsonl not found under {args.run_dir}")

    works = load_jsonl(contents_path)
    comments = load_jsonl(comments_path) if comments_path else []
    run_label = args.run_dir.name

    manifest_path = args.archive_dir / "manifest" / f"{args.account}-manifest.json"
    manifest = load_manifest(manifest_path)
    manifest = update_manifest(manifest, works, comments, run_label, args.full_refresh)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    full_path = args.archive_dir / f"{args.date}-{args.account}-douyin-full-ledger.md"
    analysis_path = args.archive_dir / f"{args.date}-{args.account}-douyin-review-analysis.md"
    latest_path = args.archive_dir / f"latest-{args.account}-summary.md"

    write_text(full_path, build_full_ledger(works, comments, args.date, run_label))
    write_text(analysis_path, build_analysis(works, comments, args.date))
    write_text(latest_path, build_latest_summary(manifest, args.date))

    print(json.dumps({
        "works": len(works),
        "comments": len(comments),
        "manifest_total_works": manifest.get("total_works", 0),
        "manifest_total_known_comments": manifest.get("total_known_comments", 0),
        "new_works": manifest.get("last_run", {}).get("new_works", 0),
        "new_comments": manifest.get("last_run", {}).get("new_comments", 0),
        "full_ledger": str(full_path),
        "review_analysis": str(analysis_path),
        "latest_summary": str(latest_path),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
