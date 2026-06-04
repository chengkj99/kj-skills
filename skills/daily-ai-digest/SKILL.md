---
name: daily-ai-digest
description: 每日 AI 前沿日报（WebSearch 采集 + 结构化定稿 + 网站自动发布）。搜索过去 24h 内 OpenAI/Anthropic/DeepMind 等机构动态及 Karpathy/LeCun/Mollick 等大 V 观点，经 P0/P1/P2 价值分级和去重后，输出面向程序员的中文日报，并自动更新网站数据。触发词：「AI 日报」「出日报」「今天 AI 有什么大事」「每日 AI 动态」「ai-daily-digest」。
---

# AI 前沿日报技能（daily-ai-digest）

**实现细节**：[`references/scoring-rubric.md`](references/scoring-rubric.md)  
**输出格式规范**：[`references/compose-format.md`](references/compose-format.md)  
**部署集成说明**：[`references/deployment.md`](references/deployment.md)

---

## 目标

把「今日值得程序员关注的 AI 动态」压缩为**可执行、可复盘、可分享**的一页中文日报，自动写入网站，最大化信噪比，零模板空话。

---

## 技能执行总则

激活本技能后，默认交付物：

| 产物 | 说明 |
|------|------|
| `content/daily/YYYY-MM-DD.md` | 完整可读日报，写入网站仓库 |
| 网站数据更新 | 自动调用 `update-daily-digest.mjs` |
| 部署提示 | 告知一条命令完成网站上线 |

| 用户意图 | 你要做的 |
|----------|----------|
| 「出日报」「AI 日报」（未限定） | 阶段 1（采集）→ 阶段 2（定稿）→ 阶段 3（写入+更新） |
| 「根据已有内容写日报」「定稿」 | 仅阶段 2+3（前提：已有原始内容） |
| 「只采集」「给我今日 AI 原始信息」 | 仅阶段 1，明确告知用户这是草稿 |

---

## 执行流程

### 阶段 1：信息采集（5-8 次 WebSearch）

搜索过去 24 小时内的最新动态，覆盖以下维度：

| 搜索方向 | 示例关键词 |
|----------|-----------|
| 机构公告 | "OpenAI announcement today", "Anthropic news today" |
| 模型/产品 | "new AI model released today", "LLM release [month year]" |
| 工具更新 | "Claude update", "Gemini update", "ChatGPT update today" |
| 大 V 动态 | "Karpathy twitter today", "Ethan Mollick post today" |
| 研究突破 | "AI research paper today", "DeepMind announcement" |
| 行业新闻 | "AI funding news", "AI company news today" |

**重点追踪来源：**
- 机构：OpenAI / Anthropic / Google DeepMind / Meta AI / Mistral / xAI / Hugging Face
- 大 V：@karpathy @ylecun @emollick @demishassabis @drjimfan @rohanpaul_ai

### 阶段 2：价值评分与筛选（内化于判断）

按 [`references/scoring-rubric.md`](references/scoring-rubric.md) 评分，分级：

- 🔥 **P0（头条）**：重大发布/突破，建议当天行动
- 📦 **P1（重要）**：产品/工具/模型更新，本周评估
- 📌 **P2（简讯）**：趋势性信息，简要记录

**去重**：同一事件只保留最高质量一条（优先官方来源）。

### 阶段 3：生成定稿

按 [`references/compose-format.md`](references/compose-format.md) 格式输出。

**质量门禁（交付前自检）**：

- [ ] 不编造 URL、发布时间、数字、账号
- [ ] 无「补充性动态，可作为趋势参考」等空话
- [ ] 无「加入日报追踪，等待更多上下文」
- [ ] 每条「建议下一步」具体可执行（不写「持续关注」）
- [ ] 同一事件只出现一次

### 阶段 4：写入项目并更新网站数据

> 适用于集成了 `daily-ai-digest` 管线的项目（见 `references/deployment.md`）。

1. **Write 工具**：保存日报到 `<APP_DIR>/content/daily/YYYY-MM-DD.md`
2. **Bash 工具**：执行数据更新：
   ```bash
   APP_DIR="<项目根目录>"
   DATE=$(date +%Y-%m-%d)
   node "$APP_DIR/scripts/update-daily-digest.mjs" --date "$DATE"
   ```
3. **回复末尾**：提示用户一键部署命令：
   ```bash
   cd <APP_DIR> && pnpm daily:deploy
   ```

---

## 与 ai-daily-brief 技能的关系

| 维度 | daily-ai-digest（本技能） | ai-daily-brief |
|------|--------------------------|----------------|
| 数据源 | Web 搜索（通用，无需 token） | X API + Nitter RSS + Web（需 X_BEARER_TOKEN） |
| 运行方式 | Cowork 定时任务，每日自动 | 手动或 GitHub Actions |
| 输出集成 | 自动写入网站 + 部署 | 输出到 `output/ai-daily-brief/` |
| 适合场景 | 日常自动推送 | 深度 X 动态分析 |

两者互补：本技能负责日常运营，`ai-daily-brief` 负责深度 X 内容分析。

---

## 故障处理

| 情况 | 处理方式 |
|------|---------|
| 某板块确实无内容 | 跳过该板块，不强行填充 |
| 搜索信息量少 | 导读注明「今日信号偏弱」，精选写相对有价值的内容 |
| Bash 执行失败 | 告知用户手动运行命令，不影响日报内容交付 |
