---
description: 列出 kj-skills 插件内各 skill 的用途与 skills/ 下的路径
---

本插件根目录下 `skills/` 包含：

| 目录 | 用途 |
|------|------|
| `wiki-doc-sink` | 个人 Wiki 沉淀（`references/` 路由 + SCHEMA/CLAUDE 约束；非当前项目 docs） |
| `ai-daily-from-x` | 每日 AI 情报日报（名单 + 采集脚本） |
| `content-creator` | 长文 / 短视频 / 小红书等内容创作工作流 |
| `weekly-report` | AI 编程领域周报采集与多格式输出 |
| `markdown-format` | Pandoc/Word 导出稿整理为 Obsidian 友好 GFM（表格分隔行、代码块、标题） |
| `git-push` | 用户明确要求时：暂存、生成 Conventional Commits 说明、提交并推送 |

请用 **Read** 打开对应目录中的 `SKILL.md` 再执行。若用户未 @ 某 skill，wiki-doc-sink 可能带 `disable-model-invocation`，以各 SKILL frontmatter 为准。
