---
name: content-growth-review
description: Analyze updated creator media data after incremental crawls and turn it into content growth diagnosis, direction adjustments, and complete topic planning. Use when the user asks to复盘抖音/视频号/公众号/小红书数据, 分析为什么涨粉弱或互动异常, 做内容增长计划, 从评论生成选题, 更新 raw/studio/funnel/backlog/manual topic pools, or plan the next publishing direction after running kangjian-douyin-media or other platform archives.
---

# Content Growth Review

Use this skill after media data has been updated. It is the analysis layer, not the crawler.

- Use `$kangjian-douyin-media` or another platform collector first to refresh raw data.
- Use this skill to diagnose growth problems, decide content direction, and produce topic plans.
- Default workspace is the LLM Wiki repo.
- Default review output path: `raw/studio/funnel/reviews/`.
- Default topic output path: `raw/studio/funnel/backlog/manual/`.

## Core Workflow

1. Collect the latest inputs with `scripts/collect_growth_inputs.py`.
2. Read the generated input bundle and any referenced source reports.
3. Diagnose data problems by separating:
   - content-market fit
   - topic clarity
   - account positioning
   - hook/opening strength
   - format and series continuity
   - comment-to-follow conversion
   - product/course/community conversion
4. Produce a review report.
5. Convert high-value findings into topic suggestions.
6. Write selected topic pools to `raw/studio/funnel/backlog/manual/` unless the user only wants chat advice.

## Quick Start

```bash
python3 <skill_dir>/scripts/collect_growth_inputs.py \
  --wiki-root "<wiki-root>" \
  --platform douyin \
  --output "/tmp/content-growth-review-inputs.md"
```

Then read `/tmp/content-growth-review-inputs.md` and the linked source files.

## Required Reads

Always check the relevant files if they exist:

- `raw/studio/funnel/published/<platform>/latest-*.md`
- latest `raw/studio/funnel/published/<platform>/*review-analysis.md`
- latest `raw/studio/funnel/published/<platform>/*full-ledger.md` only when comment examples or exact work details are needed
- `raw/studio/funnel/backlog/manual/`
- `raw/studio/funnel/backlog/queue.md`
- `wiki/playbooks/topic-bank/series-planning.md`

For Douyin, also check:

- `raw/studio/funnel/published/douyin/manifest/*.json` if present
- `raw/studio/funnel/published/douyin/runs/` when comparing snapshots

## Review Report Contract

Write a dated Markdown report when doing a real review:

```text
raw/studio/funnel/reviews/YYYY-MM-DD-<platform>-content-growth-review.md
```

Include these sections:

1. `# <平台>内容增长复盘`
2. `## 数据范围`
3. `## 本次最重要结论`
4. `## 数据异常与问题诊断`
5. `## 内容支柱表现`
6. `## 账号定位与关注理由`
7. `## 评论洞察`
8. `## 内容调整建议`
9. `## 后续方向规划`
10. `## 完整选题建议`
11. `## 本周建议晋升`
12. `## 下次增量更新要观察什么`

Use concise tables for topic suggestions. Every recommended topic should include:

- topic/title
- target audience
- source signal
- published connection
- series position
- expected metric
- first hook
- next episode hook
- whether it should enter `manual/` or `queue.md`

## Topic Pool Contract

When updating `raw/studio/funnel/backlog/manual/`, create one dated topic-pool file instead of scattering many tiny files:

```text
raw/studio/funnel/backlog/manual/YYYY-MM-DD-<platform>-growth-topics.md
```

Use frontmatter compatible with the local manual backlog:

```yaml
---
title: "..."
source: manual
pillar: ai-coding
platform: shipin
kind: funnel
status: idea
lesson_id: ~
snippet_link: ~
formatted_link: ~
published_link: ~
priority: 1
notes: "..."
---
```

Do not edit `queue.md` unless the user explicitly asks to queue items for this week. If queueing, keep the number small: 1-3 items.

## Analysis Heuristics

Interpret metrics by intent:

- High saves: utility, tutorial value, future use.
- High comments: controversy, confusion, unmet need, identity tension.
- High shares: social proof or useful decision aid.
- High likes but low saves/comments: entertaining or agreeable, weaker conversion.
- High comments but low saves: debate/情绪; useful for attention but may not convert.
- High saves but low comments: tutorial/reference; useful for course and资料包 conversion.

For growth diagnosis, distinguish:

- `曝光问题`: topic/hook/distribution may be weak.
- `互动问题`: claim is not concrete or not emotionally loaded.
- `关注问题`: account promise is unclear or content types feel scattered.
- `转化问题`: CTA,资料包,群聊,课程 promise is not connected to the video topic.
- `系列问题`: strong videos do not naturally tell users what comes next.

## Kangjian Positioning

Current strategic direction:

> 帮想用 AI 编程的人，把想法真正做成产品。

Audience is broader than programmers:

- programmers improving AI coding productivity
- non-technical vibe coding users
- independent makers and small founders
- product/operations people building MVPs
- creators turning workflows into products

Prefer using `AI 编程产品实战` as the mother theme. Treat `AI 编程教程实战` as the method library and `自媒体内容创作工作流` as proof/case material.

## Relationship To Other Skills

- Use `$kangjian-douyin-media` first when the user asks to update Douyin data.
- Use `$content-growth-review` after data exists and the user asks for复盘、增长计划、内容调整、选题建议.
- Use `$local-stt-transcription` when review conclusions require missing video transcripts.

## Validation

Before final response:

1. Confirm the reviewed source files and platform.
2. Run `git diff --check` on changed review/topic files.
3. Report every file created or updated.
4. If `queue.md` was not edited, say that topics remain in `status: idea`.
