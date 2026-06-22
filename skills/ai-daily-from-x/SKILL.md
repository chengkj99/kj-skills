---
name: ai-daily-from-x
description: 每日 AI 情报日报（采集 + 可读定稿）。汇总 skill 内置账号名单（`assets/ai-influencers-list.md` 与 `assets/follow-builders-x-handles.json`）中 X 账号昨日动态，经去重、评分、P0/P1/P2 分级后输出中文可读日报。仅在明确提到 X / 深度时触发：「X 日报」「X 昨日动态」「深度 AI 日报」「根据 raw 写可读版」「ai-daily-from-x 定稿」（通用「AI 日报」默认走 ai-daily-websearch）。阶段 1 用脚本（X API / Nitter / Web 回退）；阶段 2 由本技能 Agent 读 raw 覆盖 MD（必读 compose-readable-daily.md）。
---

# AI 日报生成技能

## 目标

把「昨日值得关注的 AI 动态」压缩成**可执行、可复盘、可转发**的一页中文日报，避免信息噪声与模板空话。

**实现细节**：[`references/implementation.md`](references/implementation.md)  
**评分规则**：[`references/scoring-rubric.md`](references/scoring-rubric.md)  
**阶段 2 定稿规范（必读）**：[`references/compose-readable-daily.md`](references/compose-readable-daily.md)

---

## 技能执行总则（Agent 必读）

激活本技能后，默认交付物是 **`output/ai-daily-from-x/daily_{YYYYMMDD}.md` 可读定稿**，不是草稿 MD。

| 用户意图 | 你要做的 |
|----------|----------|
| 「生成 / 写 / 出 AI 日报」（未限定只要采集） | **阶段 1 → 阶段 2** 一气呵成 |
| 「根据 raw 写可读版」「覆盖 daily_*.md」「定稿」 | 仅 **阶段 2**（前提：对应 `*.raw.json` 已存在） |
| 「只采集」「只要事实包」「skip compose」 | 仅 **阶段 1**，并明确告知用户 MD 仍为草稿 |

**禁止**：阶段 1 跑完后把草稿 MD 当终稿交给用户；**禁止**修改 `*.raw.json`。

---

## 输入约定

- 账号主名单：**skill 内置** `assets/ai-influencers-list.md`（随 skill 分发，自包含）。可用 `--input <路径>` 覆盖为自己的名单。
- **follow-builders 扩展名单（默认合并）**：**skill 内置** `assets/follow-builders-x-handles.json`（`parse_accounts.py` 与主名单按小写去重合并，主名单顺序优先）。可用 `--merge-json <路径>` 覆盖，或 `--no-merge` 跳过。
- 时间窗口：默认北京时间昨日 00:00:00–23:59:59
- 输出目录：`output/ai-daily-from-x/`（相对运行时当前目录）

### 环境变量（阶段 1）

- `X_BEARER_TOKEN`、`NITTER_HOSTS`、`REPORT_DATE`、`REPORT_TZ`
- `TOP_N`（默认 20）、`MIN_SCORE`（默认 6.0）、`MD_APPENDIX_LIMIT`
- 英译中（可选）：`OPENROUTER_API_KEY`、`OPENROUTER_MODEL`、`OPENROUTER_BASE_URL`、`TRANSLATE_*`、`SKIP_TRANSLATE=1`

---

## 执行流程

```text
┌─────────────────────────────────────────────────────────┐
│ 1. 解析日期 → daily_{YYYYMMDD}.raw.json 是否存在？       │
└───────────────────────────┬─────────────────────────────┘
                            │
         不存在 / 用户要求重采 ──► 阶段 1（pnpm daily:generate）
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 阶段 2：读 raw + rubric（+ 可选名单语境）              │
│    按 compose-readable-daily.md 覆盖 daily_*.md        │
│    交付前跑质量门禁自检                                   │
└─────────────────────────────────────────────────────────┘
```

### 阶段 1：采集与事实包（headless，无点评 LLM）

1. 仓库根执行：`pnpm daily:generate`（或等价调用 `scripts/run-daily-brief.sh`）。
2. 产出：
   - `daily_{YYYYMMDD}.raw.json`（事实包，`schema: ai-daily-from-x-raw-v1`）
   - `daily_{YYYYMMDD}.md`（**草稿**，待本技能覆盖）

脚本内部：`parse_accounts.py` → `build_daily_report.py`（X API → Nitter RSS → Web 搜索；规则评分、去重；可选英译中）。

### 阶段 2：可读定稿（本技能内置，Agent 执行）

**开始前**：完整阅读 [`references/compose-readable-daily.md`](references/compose-readable-daily.md)。

**输入（只读）**：

| 文件 | 用途 |
|------|------|
| `output/ai-daily-from-x/daily_{YYYYMMDD}.raw.json` | `all_candidates`、`observation_top_n`、`selected`、`stats` |
| `references/scoring-rubric.md` | 分级与去重 |
| `assets/ai-influencers-list.md`（可选） | 账号身份一句语境 |

**步骤**：

1. 读 raw 的 `date`、`stats`、`selected`、`observation_top_n`；再按需扫 `all_candidates` 全文。
2. 选材：优先 `selected` + `observation_top_n`；从 `all_candidates` 按分数与 `topic_hints` 补至 **10–15 条**「今日精选」。若全体 `< min_score`，导读写明「今日信号偏弱 / 观察级」，精选仍可低于分数线。
3. **覆盖写入** `daily_{YYYYMMDD}.md`，结构见 compose 文档（今日导读 → 今日精选 → 更多动态 ≤30 条 → 采集说明）。
4. **质量门禁**（交付前逐项自检，见 compose 文档）：
   - 无「补充性动态，可作为趋势参考」等空话
   - 无「加入日报追踪，等待更多上下文」除非正文确实不足且写明缺什么
   - 「建议下一步」与正文一致（不因出现 `repo` 就建议 clone）
   - 不编造 url、时间、账号；同事件只保留一条
5. **可选**：回写 `daily_{YYYYMMDD}.json`，含 `composed_by: ai-daily-from-x-skill`、`composed_at`、精选条目的 `headline_zh` / `value_comment` / `action_suggestion`。

**对用户回复**：说明定稿路径、精选条数、是否低分观察日、是否跳过阶段 1。

---

## 输出格式

### 终稿：`daily_{YYYYMMDD}.md`（阶段 2 覆盖）

读者 3–5 分钟可掌握「昨日 AI 编程圈值得盯什么、能做什么」。结构细则见 `compose-readable-daily.md`。

### 事实包：`daily_{YYYYMMDD}.raw.json`（阶段 1，只读）

- `selected`：达 `MIN_SCORE` 的脚本入选（可为空）
- `observation_top_n`：低分日优先阅读列表
- `all_candidates`：无 `value_comment` / `action_suggestion`

### 草稿：`daily_{YYYYMMDD}.md`（阶段 1，将被覆盖）

采集摘要 + 候选索引 + 技能定稿提示。

### 可选：`daily_{YYYYMMDD}.json`

机器可读精选 + 技能点评字段。

---

## 质量要求

- 不编造链接、发布时间、账号信息。
- 价值说明必须落到「程序员下一步能做什么」。
- 相同事件多来源只保留一条，优先官方链接。
- 输出中文，专业术语保留英文。

---

## 与本仓库命令的关系

| 命令 | 作用 |
|------|------|
| `pnpm daily:generate` | 仅阶段 1（定时 / 晨报脚本用） |
| 激活 **ai-daily-from-x** 技能 | 默认阶段 1（若需要）+ **阶段 2 定稿** |

> 注：`pnpm daily:generate` 是宿主项目可选的便捷封装；skill 本身用 `python3 scripts/...` 即可独立运行。
