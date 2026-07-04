#!/usr/bin/env python3
"""Collect latest creator-growth review inputs from the LLM Wiki workspace."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable


def latest(paths: Iterable[Path]) -> Path | None:
    items = sorted(paths, key=lambda p: (p.stat().st_mtime, str(p)))
    return items[-1] if items else None


def read_head(path: Path, max_lines: int = 80) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[:max_lines])


def grep_counts(text: str) -> list[str]:
    patterns = [
        r"- 作品数：\d+",
        r"- 一级评论数：\d+",
        r"- 总点赞：\d+",
        r"- 总评论：\d+",
        r"- 总收藏：\d+",
        r"- 总分享：\d+",
    ]
    found: list[str] = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text))
    return [item.removeprefix("- ").strip() for item in found]


def list_files(root: Path, max_count: int = 20) -> list[Path]:
    if not root.exists():
        return []
    files = sorted([p for p in root.glob("*") if p.is_file()], key=lambda p: p.name)
    return files[:max_count]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-root", type=Path, default=Path.cwd())
    parser.add_argument("--platform", default="douyin")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wiki = args.wiki_root.resolve()
    published = wiki / "raw" / "studio" / "funnel" / "published" / args.platform
    backlog = wiki / "raw" / "studio" / "funnel" / "backlog"

    review = latest(published.glob("*review-analysis.md"))
    ledger = latest(published.glob("*full-ledger.md"))
    latest_summary = latest(published.glob("latest-*.md"))
    manifests = list_files(published / "manifest", max_count=5)
    manual_files = list_files(backlog / "manual", max_count=30)
    queue = backlog / "queue.md"
    series_planning = wiki / "wiki" / "playbooks" / "topic-bank" / "series-planning.md"

    sections: list[str] = [
        f"# Content Growth Review Inputs: {args.platform}",
        "",
        "## Source Files",
        f"- platform archive: `{published}`",
        f"- latest review-analysis: `{review}`" if review else "- latest review-analysis: missing",
        f"- latest full-ledger: `{ledger}`" if ledger else "- latest full-ledger: missing",
        f"- latest summary: `{latest_summary}`" if latest_summary else "- latest summary: missing",
        f"- queue: `{queue}`" if queue.exists() else "- queue: missing",
        f"- series planning: `{series_planning}`" if series_planning.exists() else "- series planning: missing",
        "",
    ]

    if review:
        review_text = review.read_text(encoding="utf-8", errors="replace")
        sections.extend(["## Metric Snapshot", *[f"- {item}" for item in grep_counts(review_text)], ""])
        sections.extend(["## Latest Review Head", "```markdown", read_head(review, 120), "```", ""])

    if latest_summary:
        sections.extend(["## Latest Summary Head", "```markdown", read_head(latest_summary, 80), "```", ""])

    if manifests:
        sections.append("## Manifest Files")
        for manifest in manifests:
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                sections.append(f"- `{manifest}`: total_works={data.get('total_works')}, total_known_comments={data.get('total_known_comments')}, last_run={data.get('last_run', {}).get('run_id')}")
            except Exception as exc:  # noqa: BLE001
                sections.append(f"- `{manifest}`: unreadable ({exc})")
        sections.append("")

    sections.append("## Manual Topic Pools")
    for path in manual_files:
        sections.append(f"- `{path}`")
    sections.append("")

    if queue.exists():
        sections.extend(["## Queue Head", "```markdown", read_head(queue, 80), "```", ""])

    if series_planning.exists():
        sections.extend(["## Series Planning Head", "```markdown", read_head(series_planning, 80), "```", ""])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
