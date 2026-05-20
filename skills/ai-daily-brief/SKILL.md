---
name: ai-daily-brief
description: 每日 AI 情报日报生成技能。用于每天汇总 `docs/AI大佬名单.md` 中 X 账号在昨日的动态，完成去重、价值识别、P0/P1/P2 分级和中文输出。当用户提到「AI 日报」「每日情报」「6点自动汇总」「X 昨日动态」等场景时使用。支持 X API 优先、Nitter RSS 与 Web 搜索回退。
---

# AI 日报生成技能

## 目标

把「昨日值得关注的 AI 动态」压缩成可执行、可复盘、可转发的一页日报，避免信息噪声。

**实现细节（架构、数据流、采集原理、评分与排错）**：见 [`references/implementation.md`](references/implementation.md)。价值维度与权重文字说明见 [`references/scoring-rubric.md`](references/scoring-rubric.md)。

## 输入约定

- 账号源文件：`docs/AI大佬名单.md`
- 时间窗口：默认「北京时间昨日 00:00:00 - 23:59:59」
- 输出目录：`output/ai-daily-brief/`

可选环境变量：

- `X_BEARER_TOKEN`：X API 令牌（主采集路径；若接口返回 402 等表示当前套餐不可用，将自动走回退）
- `NITTER_HOSTS`：Nitter 实例列表，逗号分隔（默认 `nitter.net`）
- `REPORT_DATE`：指定统计日期（格式 `YYYY-MM-DD`，不传则自动取昨日）
- `REPORT_TZ`：时区（默认 `Asia/Shanghai`）
- `TOP_N`：最多输出条目数（默认 20）
- `MIN_SCORE`：最低分阈值（默认 6.0）
- `MD_APPENDIX_LIMIT`：Markdown 附录表格行数上限（默认 40，未达分数线与 TOP_N 截断项）
- **英译中（可选）**
  - `OPENROUTER_API_KEY`：配置后会对去重后的每条候选调用 OpenRouter（OpenAI 兼容 `chat/completions`）生成 `text_zh`；未配置时 `text_zh` 为空字符串
  - `OPENROUTER_MODEL`：默认 `openai/gpt-4o-mini`
  - `OPENROUTER_BASE_URL`：默认 `https://openrouter.ai/api/v1`
  - `OPENROUTER_HTTP_REFERER` 或 `SITE_URL`：OpenRouter 建议填站点 URL（可选）
  - `TRANSLATE_MAX_CHARS`：单条正文最多翻译字符数（默认 8000，超出部分截断并附说明）
  - `TRANSLATE_SLEEP_SEC`：两次翻译请求间隔秒数（默认 0.15，减轻限流）
  - `SKIP_TRANSLATE=1`：强制跳过翻译（与脚本 `--skip-translate` 等价）

## 执行流程

1. 运行 `scripts/parse_accounts.py`，从名单中提取有效 `@handle`。
2. 运行 `scripts/build_daily_report.py`，执行以下流程：
   - 按时间窗口采集帖子（X API 优先；若连续遇到 401/402 则跳过后续 API 请求，避免限流）。
   - API 无结果时，按时间窗过滤 **Nitter RSS**；仍无结果时再尝试 Web 搜索回退。
   - 基于 `references/scoring-rubric.md` 评分并分级（P0/P1/P2）。
   - 去重后对候选批量填充 `text_zh`（相同正文按 hash 复用译文）。
   - 按 `MIN_SCORE` 与 `TOP_N` 裁剪入选条。
   - 输出 Markdown 与 JSON 两份结果。

## 输出格式

### Markdown 日报

文件：`output/ai-daily-brief/daily_[YYYYMMDD].md`

必须包含：

- 执行摘要（采集账号数、命中条数、数据来源占比）
- 高价值条目（按 P0 -> P1 -> P2）
- 每条含：事件标题、账号、时间、原文链接、价值点评、行动建议、分数、完整正文、**中文译文**（有密钥且成功时）
- 空结果时明确写出「今日无高价值更新」

### JSON 明细

文件：`output/ai-daily-brief/daily_[YYYYMMDD].json`

必须包含：

- 运行参数与时间窗口
- 采集统计（API/回退数量、失败原因）
- 全量候选条目与评分明细（每条含原文 `text` 与 `text_zh`）
- 最终入选条目列表
- `stats.translation`：是否配置密钥、`text_zh` 非空条数、所用模型

## 质量要求

- 不编造链接、发布时间、账号信息。
- 价值点评必须落到「程序员下一步能做什么」。
- 相同事件多来源只保留一条，优先官方链接。
- 输出使用中文，术语保留英文。
