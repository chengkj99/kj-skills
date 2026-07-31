# 沉淀路由

先服从目标仓库的 `AGENTS.md`、`CLAUDE.md`、Schema 与只追加规则。下表是默认语义，不覆盖本地规范。

| 产物 | 通用去向 | LLM Wiki 常见去向 |
|---|---|---|
| 原始录音 | 私有附件目录 | `raw/assets/events/YYYYMMDD-主题/` |
| 原始转写 | 原始记录目录 | `raw/notes/events/YYYYMMDD-主题-文字稿.md` |
| 整理稿 | 与原始转写并列 | `raw/notes/events/YYYYMMDD-主题-整理稿.md` |
| 事件纪要 | 事件记录目录 | `raw/notes/events/YYYYMMDD-主题-纪要.md` |
| 单源摘要 | 来源摘要 | `wiki/sources/` |
| 单次深读 | 分析目录 | `wiki/analysis/` |
| 跨录音模式 | 综合目录 | `wiki/synthesis/` |
| 稳定概念 | 概念目录 | `wiki/concepts/` |
| 可执行方法 | Playbook 目录 | `wiki/playbooks/` |
| 选题种子 | 选题池 | `wiki/playbooks/topic-bank/seeds/` 或人工 backlog |
| 正式经营决策 | 决策/OS | 先写 inbox 或待确认状态，不替用户确认 |

## 写入门禁

1. 不因读到附件就自动复制进仓库。
2. 不编辑或覆盖原始录音、原始转写。
3. 目标 `raw/` 为人类主写时，只提供建议路径或等待明确授权/口令。
4. 新增 Wiki 页面时，同步目标仓库要求的索引、相关页面和只追加日志。
5. 用户只说“分析”时保持只读；用户说“沉淀、写入、保存”时才执行写入。
6. 如果缺少目标路径且当前仓库不能推断，先给出结果草案，再问一个最小问题。

## 长材料三层保真

对长会议、长访谈或多说话人对话，避免只有一页摘要：

- `sources`：3–5 条可检验要点和导航。
- `analysis`：按说话人/章节密抽取观点、案例、分歧和锚点。
- `synthesis`：跨议题张力、行动与结论，不重复分析明细。

所有 Wiki 层都必须能链回原始转写；摘要不能成为唯一真相源。
