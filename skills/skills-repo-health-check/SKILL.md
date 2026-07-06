---
name: skills-repo-health-check
description: Audit and improve Agent Skills repositories. Use when the user asks to check a skills repo, assess skill quality, find duplicate or overlapping skills, review SKILL.md/frontmatter/description quality, verify README or plugin index sync, compare against high-quality skill repository practices, or produce a prioritized plan to evolve a skills collection.
---

# Skills Repo Health Check

## Overview

Audit a skills repository as a capability system, not a folder of prompts. Combine automated checks with judgment about trigger quality, workflow design, verification, discoverability, safety, and repo governance.

Use this skill for one-off audits, pre-release checks after adding or renaming skills, migration/de-duplication reviews, and periodic quality reviews.

## Workflow

1. Identify the repository root and skill directories. Prefer `skills/<skill-id>/SKILL.md`; if another layout is present, verify the real implementation path before judging.
2. Run the quick audit script when possible:

   ```bash
   python3 skills/skills-repo-health-check/scripts/audit_skills_repo.py .
   ```

   Use `--json` when another tool will consume the result.

3. Read `references/best-practices.md` before producing the final assessment. Use it as the scoring rubric and improvement checklist.
4. Inspect a representative set of weak or risky skills directly, especially any skill flagged for vague triggers, missing verification, long `SKILL.md`, missing `agents/openai.yaml`, or possible overlap.
5. Check repo-level discovery surfaces: README, contributor guide, plugin manifests, marketplace files, help commands, sync scripts, and platform-specific docs.
6. Produce a decision-ready report with scores, P0/P1/P2 issues, concrete file paths, and a staged improvement plan.

## Audit Dimensions

Score each dimension from 0-10:

- Structure consistency: canonical folders, required `SKILL.md`, optional resources only when useful.
- Trigger quality: frontmatter `description` states what the skill does and when to use it.
- Scope boundaries: each skill has one clear job and avoids becoming a catch-all workflow.
- Progressive disclosure: long guidance lives in `references/`; deterministic work lives in `scripts/`.
- Verification: the skill defines commands, evidence, output checks, or review gates.
- Output contract: generated artifacts have stable fields, sections, paths, or acceptance criteria.
- Discoverability: README, help commands, manifests, and platform docs stay synchronized.
- Duplication governance: overlaps are classified as duplicate, strong overlap, complement, or pipeline dependency.
- Safety: side effects, secrets, external services, git operations, publishing, and file writes are bounded.
- Portability: the repo can work across intended harnesses such as Codex, Claude, Cursor, or Agents.

Use this rating:

```text
90-100: benchmark quality
80-89: production ready with minor improvements
70-79: usable but governance gaps remain
60-69: fragile; prioritize cleanup before expansion
<60: do not treat as a high-quality skills repository yet
```

## Report Format

Return the audit in Chinese by default:

```markdown
## 总评
- 总分：
- 等级：
- 主要判断：

## P0 必须修
- [路径] 问题：影响：建议：

## P1 应该修
- ...

## P2 可优化
- ...

## 重复/重叠 Skill
| Skill A | Skill B | 关系 | 建议 |

## 文档与注册面缺口
- README：
- manifest：
- sync：
- 平台文档：

## 30/60/90 分钟迭代计划
- 30 分钟：
- 60 分钟：
- 90 分钟：
```

## Resources

- `scripts/audit_skills_repo.py`: deterministic structural audit for `skills/` repos.
- `references/best-practices.md`: detailed rubric derived from strong public skill repositories and local governance patterns.
