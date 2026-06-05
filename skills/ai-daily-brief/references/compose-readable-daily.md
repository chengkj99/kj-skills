# AI 日报阶段 2：可读定稿

> **本文件是 `ai-daily-brief` 技能的内置阶段，不是独立技能。**  
> 技能激活且用户未明确要求「只采集」时，Agent **必须**在阶段 1 之后执行本节流程，**覆盖** `daily_{YYYYMMDD}.md`。

阶段 1（`pnpm daily:generate`）只产出 **事实包** 与 **草稿 MD**。

## 输入（只读）

| 文件 | 用途 |
|------|------|
| `output/ai-daily-brief/daily_{YYYYMMDD}.raw.json` | 候选全文、分数、链接、`observation_top_n` |
| `references/scoring-rubric.md` | 分级与去重原则 |
| `docs/strategy/AI大佬名单.md`（可选） | 账号身份语境 |

**禁止修改** `*.raw.json`。

## 输出

| 文件 | 说明 |
|------|------|
| `output/ai-daily-brief/daily_{YYYYMMDD}.md` | **覆盖**为可读定稿 |
| `output/ai-daily-brief/daily_{YYYYMMDD}.json`（可选） | 含 `composed_by`、`selected`、每条 `headline_zh` / `value_comment` / `action_suggestion` |

## 定稿 Markdown 结构（必须）

```markdown
# AI 日报（YYYY-MM-DD）

## 今日导读
（2–4 句中文：今天主线，不堆砌 UTC 窗口）

## 今日精选
（10–15 条；无条目达 min_score 时仍写，小标题可注明「观察」）

### [中文标题一句话]
- **谁**：@handle（可加身份）
- **发生了什么**：（2–3 句中文，术语保留英文）
- **对程序员的价值**：（具体，1–2 句）
- **建议下一步**：（可执行，与正文一致）
- **链接**：url
- **分数**：score（P?）

## 更多动态
（其余候选：每行一句中文摘要 + 链接，≤30 条）

## 采集说明
（账号数、数据源、raw 路径一行即可）
```

## 质量门禁（交付前自检）

- [ ] 无「补充性动态，可作为趋势参考」
- [ ] 无「加入日报追踪，等待更多上下文」除非正文确实信息不足（并写明缺什么）
- [ ] 「建议下一步」与正文主题一致（不因出现 `repo` 就建议 clone）
- [ ] 不编造 url、时间、账号
- [ ] 同事件只保留一条

## 选材建议

1. 优先阅读 `observation_top_n` 与 `selected`。
2. 再从 `all_candidates` 按分数与 `topic_hints` 补全至 10–15 条精选。
3. 低分日（全体 < `min_score`）仍输出精选，在导读中说明「今日信号偏弱，以下为相对值得跟进的观察」。

## 反例（禁止照搬）

```text
价值点评：这是补充性动态，可作为趋势参考。
行动建议：加入日报追踪，等待更多上下文后再决策。
```

## 与阶段 1 的衔接

- 草稿 MD 顶部「待 Skill 定稿」→ 本阶段完成后应变为正式标题 `# AI 日报（日期）`，无「草稿」字样。
- `raw.json` 内 `compose_hint` 字段仅为机器提示；以本文件与 `SKILL.md` 为准。
