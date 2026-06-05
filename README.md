# kj-skills

Claude / Cursor **Agent Skills** 集合：个人 Wiki 沉淀、AI 日报、内容创作、AI 编程周报、Git 提交推送。目录结构参考 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)。

## 包含的 Skills

| 目录 | 说明 |
|------|------|
| [skills/wiki-doc-sink](skills/wiki-doc-sink/SKILL.md) | 讨论沉淀到个人 Wiki（含 `references/` 路由说明，需配置 `<WIKI_ROOT>`） |
| [skills/ai-daily-brief](skills/ai-daily-brief/SKILL.md) | 每日 AI 情报日报（脚本 + 评分 rubric） |
| [skills/content-creator](skills/content-creator/SKILL.md) | 长文 / 短视频 / 小红书等工作流 |
| [skills/weekly-report](skills/weekly-report/SKILL.md) | AI 编程周报多格式输出 |
| [skills/markdown-format](skills/markdown-format/SKILL.md) | Pandoc/Word 稿 Markdown 格式化（Obsidian 表格、代码块、标题） |
| [skills/git-push](skills/git-push/SKILL.md) | 一键 add / 生成 commit / push（Conventional Commits + 安全约束） |
| [skills/kangjian-skill](skills/kangjian-skill/SKILL.md) | 以康健本人风格创作公众号文章 / 短视频口播 / AI 编程教程 / 演讲稿（去 AI 味门禁） |

## wiki-doc-sink：配置 `WIKI_ROOT`（使用前必读）

[`wiki-doc-sink`](skills/wiki-doc-sink/SKILL.md) 会把讨论沉淀到你**个人的 LLM Wiki 仓库**，而不是当前打开项目的 `docs/`。skill 内用占位符 `<WIKI_ROOT>` 表示 Wiki 根目录——**安装插件不会自动替你填路径**，需要你在本机先声明一次。

### 前置条件

1. 已有（或新建）个人 Wiki 仓库，且根目录存在 `SCHEMA.md` 与 `CLAUDE.md`（目录规范与 Ingest 流程以这两份文件为准）。
2. 记下该仓库在本机的**绝对路径**，例如 `/Users/you/llm-wiki`。

### 设置方式（任选其一）

**Claude Code — 全局规则（推荐）**

在 `~/.claude/CLAUDE.md` 中增加（路径改成你的）：

```markdown
## 个人 Wiki（wiki-doc-sink）

- WIKI_ROOT: `/Users/you/llm-wiki`
- 使用 wiki-doc-sink 或「沉淀到文档」时，将 skill 中的 `<WIKI_ROOT>` 替换为上述路径。
- 写入前用 Read 核对：`<WIKI_ROOT>/SCHEMA.md`、`<WIKI_ROOT>/CLAUDE.md`。
```

**Cursor — User Rules 或项目规则**

在 **Cursor Settings → Rules → User Rules**，或项目 `.cursor/rules/` 下新增 alwaysApply 规则，内容与上面相同，把 `WIKI_ROOT` 写成你的绝对路径。

**Fork / 单 skill 复制 — 直接改 skill**

若只在本机使用、不依赖全局规则，可编辑 `skills/wiki-doc-sink/SKILL.md`，将文中所有 `<WIKI_ROOT>` 替换为你的绝对路径（fork 后维护即可）。

### 使用前自检

```bash
ls /Users/you/llm-wiki/SCHEMA.md /Users/you/llm-wiki/CLAUDE.md
```

两条路径都能读到，再 **@ wiki-doc-sink** 或说「沉淀到文档」。

### 未设置 `WIKI_ROOT` 时

若已 @ `wiki-doc-sink` 或触发「沉淀到文档」，但 Agent 不知道 Wiki 根目录：

1. **先停止写入**当前项目的 `docs/`、`README` 等默认落点（除非你在同一句里明确指定「就写在本仓库某路径」）。
2. 按上一节完成 `WIKI_ROOT` 配置，并确认 `SCHEMA.md` / `CLAUDE.md` 可读。
3. 重新发起沉淀请求；Agent 应按 Wiki 规范写入 `wiki/`，且 **`raw/` 只读**。

更完整的流程与约束见 [skills/wiki-doc-sink/SKILL.md](skills/wiki-doc-sink/SKILL.md) 与同目录 `references/`。

若你同时维护**组织/公司业务 Wiki**（例如信贷前端专用库），公司库路由请保留在本机 `~/.claude/rules/`，本仓库 skill 仅覆盖个人 `<WIKI_ROOT>`。

## Claude Code：Marketplace 安装（推荐）

将下列 `chengkj99/kj-skills` 换成你 fork 后的 `owner/repo`，并同步修改 `.claude-plugin/marketplace.json` 里 `plugins[0].source.repo`（否则 marketplace 仍指向原仓库）：

```text
/plugin marketplace add chengkj99/kj-skills
/plugin install kj-skills@ck-agent-skills
```

若 marketplace 克隆走 SSH 报错，可改用 HTTPS 添加源：

```text
/plugin marketplace add https://github.com/chengkj99/kj-skills.git
/plugin install kj-skills@ck-agent-skills
```

安装后可使用插件命令 **`/ck-help`** 快速查看各 skill 路径。

## Claude Code：本地克隆 + 插件目录

```bash
git clone https://github.com/chengkj99/kj-skills.git
claude --plugin-dir /path/to/kj-skills
```

`--plugin-dir` 指向**仓库根目录**（包含 `.claude-plugin` 的那一层）。

## Cursor：插件安装

仓库已包含 `.cursor-plugin/` 清单，支持 Cursor 插件体系（与 Claude Code 的 `.claude-plugin/` 并存）。

| 场景 | 做法 |
|------|------|
| 本地调试 | `ln -s /path/to/kj-skills ~/.cursor/plugins/local/kj-skills`，重启 Cursor |
| 团队分发 | Dashboard → Plugins → Team Marketplaces → Import `https://github.com/chengkj99/kj-skills` |
| 公开发布 | 提交 [Cursor Marketplace](https://cursor.com/marketplace/publish) 审核后，对话中 `/add-plugin kj-skills` |

**不要在 Cursor 里执行** `/plugin marketplace add`（那是 Claude Code 命令）。详见 [docs/cursor-setup.md](docs/cursor-setup.md)。

## 单 skill 安装

只需某一目录时，将 `skills/<skill-name>/` **整个文件夹**复制到 Cursor 项目 `.cursor/skills/<skill-name>/` 或全局 skills 目录（见 `docs/cursor-setup.md`）。

## 许可证

MIT，见 [LICENSE](LICENSE)。
