#!/usr/bin/env python3
"""
将 Pandoc/杂乱 Markdown 整理为 Obsidian 友好的 GFM。
默认原地写回；--check 仅报告表格缺分隔行数量。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def col_count(row: str) -> int:
    parts = [p for p in row.strip().split("|")]
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return len(parts)


def is_separator(row: str) -> bool:
    s = row.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    return all(re.fullmatch(r":?-{3,}:?", c or "---") for c in cells)


def fix_table_separators(text: str) -> tuple[str, int]:
    """在表头后插入 | --- | 分隔行。返回 (新文本, 修复表数)。"""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    fixed = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and line.strip().endswith("|"):
            block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                block.append(lines[i])
                i += 1
            if block:
                out.append(block[0])
                n = col_count(block[0])
                sep = "| " + " | ".join(["---"] * n) + " |"
                if len(block) > 1 and is_separator(block[1]):
                    out.extend(block[1:])
                else:
                    out.append(sep)
                    out.extend(block[1:])
                    fixed += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out), fixed


def tighten_callout_lists(text: str) -> str:
    return re.sub(r"(^> - .+)\n\n(?=> - )", r"\1\n", text, flags=re.M)


def main() -> int:
    parser = argparse.ArgumentParser(description="GFM/Obsidian Markdown 表格分隔行修复等")
    parser.add_argument("path", type=Path, help="目标 .md 文件")
    parser.add_argument("--check", action="store_true", help="只检查，不写回")
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"错误：文件不存在 {args.path}", file=sys.stderr)
        return 1

    original = args.path.read_text(encoding="utf-8")
    text, fixed = fix_table_separators(original)
    text = tighten_callout_lists(text)

    if args.check:
        print(f"需补分隔行的表格约: {fixed} 处")
        return 0

    if text != original:
        args.path.write_text(text, encoding="utf-8")
        print(f"已写回 {args.path}（补分隔行 {fixed} 处，并收紧引用块列表空行）")
    else:
        print(f"无变化: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
