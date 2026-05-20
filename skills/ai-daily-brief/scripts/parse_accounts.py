#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def extract_handles(markdown_text: str) -> list[str]:
    # 优先从链接中提取 handle，准确率更高。
    link_handles = re.findall(r"twitter\.com/([A-Za-z0-9_]{1,15})", markdown_text, flags=re.IGNORECASE)
    plain_handles = re.findall(r"(?<![A-Za-z0-9_])@([A-Za-z0-9_]{1,15})", markdown_text)
    merged: list[str] = []
    for raw in link_handles + plain_handles:
        handle = raw.strip().lstrip("@")
        if not handle:
            continue
        lower = handle.lower()
        if lower in {"twitter", "x", "nvidia"}:
            # 保留 nvidia 官方账号作为候选，后续不会在这里强行过滤。
            pass
        if handle not in merged:
            merged.append(handle)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="从 AI 大佬名单 Markdown 提取 X 账号")
    parser.add_argument(
        "--input",
        default="docs/AI大佬名单.md",
        help="输入 Markdown 文件路径",
    )
    parser.add_argument(
        "--output",
        default="output/ai-daily-brief/accounts.json",
        help="输出 JSON 文件路径",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    handles = extract_handles(text)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "source_file": str(input_path),
                "total_handles": len(handles),
                "handles": handles,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"已提取 {len(handles)} 个账号 -> {output_path}")


if __name__ == "__main__":
    main()
