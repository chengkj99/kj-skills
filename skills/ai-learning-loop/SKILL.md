---
name: ai-learning-loop
description: This skill should be used when the user asks to "跑一轮学习闭环", "用卡片阅读法处理这份材料", "我想学习 X 但没有资料", "帮我调研 X 的学习资源", "给我一个最小阅读包", "把这个主题变成一张表达卡片", or wants to turn a topic, article, course, note, or idea into a focused AI-assisted learning loop with a real question, optional resource research, an expression card, review feedback, and wiki/card sink decisions.
---

# AI Learning Loop

Run a compact learning workflow that turns a topic or material into a concrete output and a small number of reusable knowledge cards. Optimize for feedback density, not note volume.

## Core Loop

Use this sequence:

```text
learning goal
  -> real question
  -> minimal input or research pack
  -> expression card
  -> output review
  -> one necessary card/sink decision
  -> next loop question
```

Prefer one loop at a time. Do not turn the task into a broad research report or a large note-taking project unless the user explicitly asks.

## Workflow

### 1. Clarify the learning target

Identify the user's intended output before collecting or summarizing information.

If the target is unclear, ask one concise question. Otherwise infer a practical target from context, such as a口播稿、公众号段落、课程小节、playbook、咨询框架, or decision memo.

Read `references/question-planning.md` when the request starts from a broad topic, has no material, or needs a minimal learning path.

### 2. Decide the input path

Choose one:

| Situation | Action |
|---|---|
| User provided material | Use that material as the first input. |
| Material exists in a wiki/repo | Search the local wiki/repo first, then read the closest sources. |
| User has no material | Build a minimal research pack before writing the expression card. |
| Topic is current or unstable | Use web search or official/current sources when available; mark any source-quality caveats. |

For no-material requests, do not gather many links. Produce a smallest useful pack: 3 must-read resources, up to 5 optional resources, skip list, reading order, and first output task.

### 3. Build an expression card

Create one publishable or near-publishable expression card around one core judgment. Read `references/expression-card.md` when drafting a口播稿、短文、课程小节、or other output card.

Treat口播稿 as an expression card:

```text
raw/studio/funnel/formatted/shipin/ = pre-publish expression card
raw/studio/funnel/transcripts/ = post-publish asset card
```

If working inside `kj-llm-wiki`, follow that repo's raw/wiki rules. Do not write to `raw/` unless the user explicitly asks for a production draft and the repo rules allow that path.

### 4. Review before expanding

Review the output before polishing or expanding it. Read `references/review-and-sink.md` when judging gaps, quality, or wiki sink decisions.

The review must answer:

- Is the core judgment clear?
- Is there a real reader pain or use case?
- Which parts are generic or obvious?
- Where is the logic jump?
- What example, counterexample, boundary, or source is missing?
- What is the single most necessary card to add next?

### 5. Sink only the necessary card

Recommend at most one mandatory sink item by default:

| Gap | Sink target |
|---|---|
| Concept unclear | `wiki/concepts/` |
| Repeatable method | `wiki/playbooks/` |
| Single source summary | `wiki/sources/` |
| Heavy material needs deep reading | `wiki/analysis/` |
| Multi-source conclusion | `wiki/synthesis/` |
| Public content candidate | topic bank / studio workflow |

If the user says "沉淀到文档/知识库", invoke the existing `wiki-doc-sink` workflow rather than reimplementing wiki write rules.

## Output Contract

For one loop, return:

1. 今日真实问题
2. 最小输入/调研包
3. 表达卡片
4. 评审反馈
5. 只补哪一张卡
6. 下一轮问题

Keep the answer concise unless the user asks for a full draft or asks to write files.

## 交付前自检

- [ ] 对照 Output Contract 逐项核对回复包含全部 6 项：今日真实问题、最小输入/调研包、表达卡片、评审反馈、只补哪一张卡、下一轮问题
- [ ] 无材料请求时，清点调研包数量达标：必读资源恰好 3 个、可选资源不超过 5 个，且含 skip list、阅读顺序和首个输出任务
- [ ] 检查表达卡片只围绕一个核心判断展开，评审反馈逐条回答了第 4 步列出的 6 个问题
- [ ] 确认沉淀建议默认不超过一张必要卡片，且沉淀目标与 Gap 对照表（`wiki/concepts/`、`wiki/playbooks/` 等）一致
- [ ] 在 `kj-llm-wiki` 中执行时，确认未在用户未明确要求的情况下写入 `raw/` 目录
