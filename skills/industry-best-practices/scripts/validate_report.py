#!/usr/bin/env python3
"""行业最佳实践报告校验器。

按输出契约（brief / deep / digest）检查 Markdown 报告的章节标题是否齐全，
并检查若干全局要求（实时验证状态、MVP、指标）。使用 --strict 时还会
检查标准调研的最低信息密度，防止仅有标题或占位表格的报告通过校验。

用法：
    python3 validate_report.py report.md --contract brief
    python3 validate_report.py report.md --contract deep
    python3 validate_report.py report.md --contract digest
    python3 validate_report.py report.md --contract brief --strict

契约与模板的对应关系：
    brief  -> assets/templates/research-brief.md
    deep   -> assets/templates/deep-research-report.md
    digest -> assets/templates/daily-digest.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 每个章节用「若干关键词备选」表示：任一关键词出现在某个标题行中即视为该章节存在。
# 这样既允许标题措辞微调，又避免旧版「全文子串匹配」的误判。
CONTRACT_SECTIONS: dict[str, list[tuple[str, list[str]]]] = {
    "brief": [
        ("范围和假设", ["范围"]),
        ("结论先行", ["结论"]),
        ("信号地图", ["信号地图"]),
        ("范式/理念/架构变化", ["范式", "理念变化", "架构变化"]),
        ("重点信号解析", ["重点信号", "信号解析"]),
        ("优化建议池", ["优化建议", "建议池"]),
        ("架构/流程影响", ["架构", "流程影响"]),
        ("风险和不确定性", ["风险"]),
        ("下一步", ["下一步", "行动计划"]),
    ],
    "deep": [
        ("调研问题", ["调研问题", "研究问题"]),
        ("方法和范围", ["方法", "范围"]),
        ("查询矩阵", ["查询矩阵", "查询"]),
        ("结论先行", ["结论"]),
        ("关键发现", ["关键发现", "发现"]),
        ("论文/方法进展", ["论文", "方法进展"]),
        ("开源/工程实践", ["开源", "工程实践"]),
        ("竞品/市场动态", ["竞品", "市场动态"]),
        ("专家观点", ["专家"]),
        ("趋势判断", ["趋势"]),
        ("优化建议池", ["优化建议", "建议池"]),
        ("MVP 实验设计", ["MVP"]),
        ("架构路线图", ["架构路线", "路线图"]),
        ("风险", ["风险"]),
        ("附录：来源清单", ["来源清单", "附录"]),
    ],
    "digest": [
        ("范围", ["范围"]),
        ("Top 信号", ["Top", "信号"]),
        ("范式变化", ["范式"]),
        ("论文/方法", ["论文", "方法"]),
        ("开源项目", ["开源"]),
        ("竞品动作", ["竞品"]),
        ("机会池", ["机会池", "建议"]),
        ("噪音和风险", ["噪音", "风险"]),
        ("深挖的问题", ["深挖"]),
    ],
}

# 全局要求：在正文任意位置出现即可。
GLOBAL_MARKERS: list[tuple[str, list[str]]] = [
    ("实时验证状态", ["实时验证状态"]),
    ("MVP", ["MVP"]),
    ("指标", ["指标"]),
]

HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
URL_RE = re.compile(r'https?://[^\s)>"]+')
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$", re.MULTILINE)


def non_placeholder_rows(text: str, required_cells: int = 3) -> list[str]:
    """Return content table rows, excluding separators and unreplaced templates."""
    rows = []
    for row in TABLE_ROW_RE.findall(text):
        if "---" in row or "{{" in row:
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if sum(bool(cell) for cell in cells) >= required_cells:
            rows.append(row)
    return rows


def section_body(text: str, keyword: str) -> str:
    """Return an H2 section body so row counts do not leak across tables."""
    match = re.search(
        rf"^## [^\n]*{re.escape(keyword)}[^\n]*\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def strict_density_issues(text: str, contract: str) -> list[str]:
    """Check the minimum density promised by the standard-report contract."""
    if contract != "brief":
        return []
    issues: list[str] = []
    urls = set(URL_RE.findall(text))
    signal_rows = [
        row for row in non_placeholder_rows(section_body(text, "信号地图")) if re.search(r"S\d{3}", row)
    ]
    recommendation_rows = [
        row
        for row in non_placeholder_rows(section_body(text, "优化建议池"))
        if any(token in row for token in ("P0", "P1", "P2", "高", "中", "低"))
    ]
    detail_headings = [h for h in HEADING_RE.findall(text) if re.search(r"S\d{3}", h)]

    if len(signal_rows) < 6:
        issues.append(f"信号地图有效行不足：{len(signal_rows)}/6")
    if len(detail_headings) < 3:
        issues.append(f"重点信号解析不足：{len(detail_headings)}/3")
    if len(recommendation_rows) < 3:
        issues.append(f"优化建议有效行不足：{len(recommendation_rows)}/3")
    if len(urls) < 4:
        issues.append(f"独立来源链接不足：{len(urls)}/4")
    return issues


def validate(text: str, contract: str, strict: bool = False) -> dict:
    headings = HEADING_RE.findall(text)
    missing_sections = []
    for label, keywords in CONTRACT_SECTIONS[contract]:
        if not any(kw.lower() in h.lower() for h in headings for kw in keywords):
            missing_sections.append(label)

    missing_markers = [
        label
        for label, keywords in GLOBAL_MARKERS
        if not any(kw.lower() in text.lower() for kw in keywords)
    ]

    density_issues = strict_density_issues(text, contract) if strict else []
    return {
        "ok": not missing_sections and not missing_markers and not density_issues,
        "contract": contract,
        "headings_found": len(headings),
        "missing_sections": missing_sections,
        "missing_global_markers": missing_markers,
        "strict": strict,
        "density_issues": density_issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="校验行业最佳实践报告的章节完整性")
    parser.add_argument("path", help="Markdown 报告路径")
    parser.add_argument(
        "--contract",
        choices=sorted(CONTRACT_SECTIONS),
        default="brief",
        help="输出契约类型（默认 brief）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="校验标准调研的最低信息密度（交付真实 brief 时使用）",
    )
    args = parser.parse_args()
    text = Path(args.path).read_text(encoding="utf-8")
    result = validate(text, args.contract, args.strict)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
