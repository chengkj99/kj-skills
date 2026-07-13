#!/usr/bin/env python3
"""Quick structural audit for Agent Skills repositories."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TRIGGER_WORDS = (
    "use when",
    "when to use",
    "used when",
    "when the user",
    "trigger",
    "用户",
    "当用户",
    "适用",
    "触发",
    "时使用",
    "使用本",
    "使用此",
)

_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """解析 frontmatter，支持 YAML 块标量（>、>-、|、|-）和缩进折行。"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    lines = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(lines):
        match = _KEY_RE.match(lines[i])
        if not match:
            i += 1
            continue
        key, value = match.groups()
        parts: list[str] = []
        if value.strip() not in {">", ">-", "|", "|-", ""}:
            parts.append(value.strip())
        # 吸收缩进的续行（块标量内容或 plain scalar 折行）
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j][:1] in (" ", "\t")):
            if lines[j].strip():
                parts.append(lines[j].strip())
            j += 1
        data[key] = " ".join(parts).strip().strip('"').strip("'")
        i = j
    return data, text[end + 4 :]


def tokenize(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}|[\u4e00-\u9fff]{2,}", text.lower())
        if word not in {"skill", "skills", "when", "use", "with", "this", "that", "the"}
    }


def issue(severity: str, path: Path, message: str) -> dict[str, str]:
    return {"severity": severity, "path": str(path), "message": message}


def audit_skill(skill_file: Path, repo: Path) -> dict[str, Any]:
    folder = skill_file.parent
    rel = skill_file.relative_to(repo)
    text = skill_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    issues: list[dict[str, str]] = []

    name = fm.get("name", "")
    description = fm.get("description", "")

    if not fm:
        issues.append(issue("P0", rel, "missing YAML frontmatter"))
    if not name:
        issues.append(issue("P0", rel, "missing frontmatter name"))
    elif name != folder.name:
        issues.append(issue("P1", rel, f"name '{name}' does not match folder '{folder.name}'"))
    if not description:
        issues.append(issue("P0", rel, "missing frontmatter description"))
    else:
        lowered = description.lower()
        if len(description) < 80:
            issues.append(issue("P1", rel, "description is short; may not route reliably"))
        if not any(word in lowered for word in TRIGGER_WORDS):
            issues.append(issue("P1", rel, "description does not clearly say when to use the skill"))
    if "TODO" in text or "[TODO" in text:
        issues.append(issue("P0", rel, "template TODO text remains"))
    if len(text.splitlines()) > 500:
        issues.append(issue("P2", rel, "SKILL.md is over 500 lines; consider references/"))
    if "verification" not in body.lower() and "验证" not in body and "自检" not in body:
        issues.append(issue("P2", rel, "no obvious verification section"))
    if "output" not in body.lower() and "输出" not in body and "交付" not in body:
        issues.append(issue("P2", rel, "no obvious output contract section"))

    openai_yaml = folder / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        issues.append(issue("P2", openai_yaml.relative_to(repo), "missing agents/openai.yaml"))

    for ref in (folder / "references").glob("*.md") if (folder / "references").exists() else []:
        lines = ref.read_text(encoding="utf-8").splitlines()
        if len(lines) > 100 and not any(line.startswith("#") for line in lines[:20]):
            issues.append(issue("P2", ref.relative_to(repo), "long reference lacks early headings"))

    return {
        "name": name or folder.name,
        "folder": folder.name,
        "path": str(rel),
        "description": description,
        "issues": issues,
        "tokens": sorted(tokenize(description + "\n" + body[:2000])),
    }


def audit_repo(repo: Path) -> dict[str, Any]:
    skills_dir = repo / "skills"
    skill_files = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.exists() else []
    all_issues: list[dict[str, str]] = []
    skills = [audit_skill(path, repo) for path in skill_files]
    for skill in skills:
        all_issues.extend(skill["issues"])

    if not skills_dir.exists():
        all_issues.append(issue("P0", Path("skills"), "missing skills/ directory"))
    if not skill_files:
        all_issues.append(issue("P0", Path("skills"), "no skills/*/SKILL.md files found"))

    readme = repo / "README.md"
    if not readme.exists():
        all_issues.append(issue("P1", Path("README.md"), "missing README.md"))
    else:
        readme_text = readme.read_text(encoding="utf-8")
        for skill in skills:
            if f"skills/{skill['folder']}" not in readme_text and f"`{skill['folder']}`" not in readme_text:
                all_issues.append(issue("P2", Path("README.md"), f"{skill['folder']} not found in README"))

    for manifest in (".codex-plugin/plugin.json", ".cursor-plugin/plugin.json", ".agents/plugins/marketplace.json"):
        path = repo / manifest
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                all_issues.append(issue("P1", Path(manifest), f"invalid JSON: {exc}"))

    overlaps = []
    for index, left in enumerate(skills):
        left_tokens = set(left["tokens"])
        if len(left_tokens) < 8:
            continue
        for right in skills[index + 1 :]:
            right_tokens = set(right["tokens"])
            if len(right_tokens) < 8:
                continue
            score = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
            if score >= 0.35:
                overlaps.append(
                    {
                        "left": left["folder"],
                        "right": right["folder"],
                        "similarity": round(score, 2),
                    }
                )

    penalty = sum({"P0": 10, "P1": 3, "P2": 1}.get(item["severity"], 1) for item in all_issues)
    score = max(0, min(100, 100 - penalty))

    return {
        "repo": str(repo),
        "skill_count": len(skills),
        "score": score,
        "issues": all_issues,
        "possible_overlaps": overlaps,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Skills Repo Health Check",
        "",
        f"- Repo: `{result['repo']}`",
        f"- Skill count: {result['skill_count']}",
        f"- Structural score: {result['score']}/100",
        "",
        "## Issues",
    ]
    if result["issues"]:
        for item in result["issues"]:
            lines.append(f"- [{item['severity']}] `{item['path']}`: {item['message']}")
    else:
        lines.append("- No structural issues found by the quick audit.")

    lines.extend(["", "## Possible Overlaps"])
    if result["possible_overlaps"]:
        for item in result["possible_overlaps"]:
            lines.append(f"- `{item['left']}` <-> `{item['right']}`: similarity {item['similarity']}")
    else:
        lines.append("- No high-similarity pairs found by the quick audit.")

    lines.extend(
        [
            "",
            "Note: this script is a fast structural scan. Use the skill rubric for final judgment.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an Agent Skills repository.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    result = audit_repo(repo)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
