"""日报账号：follow-builders JSON 与主名单合并（parse_accounts / build_daily_report 共用）。"""
from __future__ import annotations

import json
from pathlib import Path


def repo_root() -> Path:
    """本文件位于 .claude/skills/ai-daily-brief/scripts/，仓库根为其上五级。"""
    return Path(__file__).resolve().parents[4]


def default_follow_builders_json() -> Path:
    return repo_root() / "docs" / "strategy" / "follow-builders-x-handles.json"


def load_extra_handles_from_json(path: Path) -> list[str]:
    """读取 follow-builders 风格 JSON：支持 x_accounts[].handle 或顶层 handles。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw.get("handles"), list):
        return [
            str(x).strip().lstrip("@")
            for x in raw["handles"]
            if x and str(x).strip()
        ]
    xs = raw.get("x_accounts") or []
    out: list[str] = []
    for row in xs:
        if not isinstance(row, dict):
            continue
        h = row.get("handle")
        if not h:
            continue
        out.append(str(h).strip().lstrip("@"))
    return out


def merge_handle_lists(primary: list[str], extra: list[str]) -> list[str]:
    """主列表顺序不变；extra 中尚未出现（大小写不敏感）的 handle 追加到末尾。"""
    seen = {h.lower() for h in primary}
    merged = list(primary)
    for h in extra:
        if not h:
            continue
        key = h.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(h)
    return merged
