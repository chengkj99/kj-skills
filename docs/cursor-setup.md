# Cursor 中使用 ck-skills

本仓库同时提供 **Cursor 插件**（`.cursor-plugin/`）与 **Claude Code 插件**（`.claude-plugin/`），skills 内容共用 `skills/` 目录。

## 方式一：插件安装（推荐）

### A. 官方市场（需审核）

向 Cursor 提交开源插件审核后，用户可在 Agent 对话或插件面板安装：

```text
/add-plugin ck-skills
```

提交入口：[cursor.com/marketplace/publish](https://cursor.com/marketplace/publish)

### B. 团队市场（Teams / Enterprise）

管理员在 **Dashboard → Settings → Plugins → Team Marketplaces → Import** 粘贴仓库地址：

```text
https://github.com/chengkj99/ck-skills
```

团队成员在 Cursor 插件面板中即可看到并安装 `ck-skills`。

### C. 本地调试（开发或未上架时）

将仓库链到 Cursor 本地插件目录后重启 Cursor（或 **Developer: Reload Window**）：

```bash
ln -s /path/to/ck-skills ~/.cursor/plugins/local/ck-skills
```

然后在 Cursor 设置 → Rules 中确认 skills 已加载，或在对话里 **@** 对应 skill。

## 方式二：仅复制单个 Skill（无需插件）

适合只要某一个能力、不想装整包的场景。

### 项目级（推荐团队协作）

1. 在项目根创建 `.cursor/skills/`（若不存在）。
2. 将 `skills/<skill-name>/` **整目录**复制到 `.cursor/skills/<skill-name>/`（含子目录，例如 `wiki-doc-sink/references/`）。
3. 在对话里 **@** 该 skill，或依赖 `SKILL.md` 中的 `description` 自动触发。

### 全局（个人所有项目）

复制到 `~/.cursor/skills/<skill-name>/`（以你本机 Cursor 版本文档为准）。

## 与 Claude Code 的区别

| 能力 | Cursor | Claude Code |
|------|--------|-------------|
| 清单目录 | `.cursor-plugin/` | `.claude-plugin/` |
| 添加市场源 | 团队市场 Import / 官方审核 | `/plugin marketplace add owner/repo` |
| 安装插件 | `/add-plugin ck-skills` 或插件面板 | `/plugin install ck-skills@ck-agent-skills` |
| 本地调试 | `~/.cursor/plugins/local/` | `claude --plugin-dir /path/to/ck-skills` |

**注意**：不要在 Cursor 里使用 `/plugin marketplace add`（那是 Claude Code 命令）；在 Cursor 插件 UI 里搜索 `chengkj99/ck-skills` 会显示 **No matching plugins**，因为那是按插件名过滤，不是添加 Git 市场源。

## 包含的 Skills

| 目录 | 说明 |
|------|------|
| `wiki-doc-sink` | 讨论沉淀到个人 Wiki（含 `references/personal-wiki-bridge.md`、`routing-notes.md`） |
| `ai-daily-brief` | 每日 AI 情报日报 |
| `content-creator` | 长文 / 短视频 / 小红书等工作流 |
| `weekly-report` | AI 编程周报 |
| `markdown-format` | Markdown / Obsidian 格式化 |
| `git-push` | 暂存、Conventional Commits 提交并推送 |

## 维护建议

以本 Git 仓库为单一事实来源；若同时用 Cursor 插件与 Claude Code 插件，升级时拉取同一仓库即可，无需分别复制 skills。
