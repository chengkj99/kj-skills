#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from account_merge import (
    default_follow_builders_json,
    default_source_md,
    load_extra_handles_from_json,
    merge_handle_lists,
)


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
        default=None,
        help="输入 Markdown 文件路径（不传则用 skill 内置 assets/ai-influencers-list.md；相对路径相对当前目录）",
    )
    parser.add_argument(
        "--output",
        default="output/ai-daily-brief/accounts.json",
        help="输出 JSON 文件路径（相对路径相对当前目录）",
    )
    parser.add_argument(
        "--merge-json",
        default=None,
        help="合并用的 JSON；默认使用仓库内 follow-builders 同步文件",
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="不合并 follow-builders 扩展 JSON，仅使用主名单 Markdown",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser() if args.input else default_source_md()
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    handles = extract_handles(text)

    merge_path = Path(args.merge_json).expanduser() if args.merge_json else default_follow_builders_json()
    if not merge_path.is_absolute():
        merge_path = (Path.cwd() / merge_path).resolve()

    merged_from_file = False
    if args.no_merge:
        print("已指定 --no-merge，跳过扩展 JSON 合并")
    elif merge_path.exists():
        extra = load_extra_handles_from_json(merge_path)
        before = len(handles)
        handles = merge_handle_lists(handles, extra)
        added = len(handles) - before
        merged_from_file = True
        if added:
            print(f"已从 {merge_path} 合并 {added} 个新账号（去重后共 {len(handles)} 个）")
        else:
            print(f"已读取 {merge_path}，无新增账号（与主名单全部重复，共 {len(handles)} 个）")
    else:
        print(f"未找到合并文件 {merge_path}，跳过 follow-builders 扩展名单")

    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "source_file": str(input_path),
                "merge_json": (
                    None
                    if args.no_merge or not merged_from_file
                    else str(merge_path)
                ),
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
