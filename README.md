# kj-skills

Claude / Cursor **Agent Skills** 集合：AI 编程内容创作全链路、个人 Wiki 沉淀、AI 日报、周报、Git 提交推送。目录结构参考 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)。

## 包含的 Skills

| 目录 | 说明 |
|------|------|
| [skills/ai-programming-topic-planner](skills/ai-programming-topic-planner/SKILL.md) | AI 编程内容选题策略：输入动态/痛点/想法，输出 3-5 个内容角度 + 推荐工作流 |
| [skills/coding-session-to-tutorial](skills/coding-session-to-tutorial/SKILL.md) | 实战记录转教程：原始命令/报错/过程 → 结构化 AI 编程教程初稿 |
| [skills/course-generator](skills/course-generator/SKILL.md) | 单章节课程正文生成：章节大纲 + 参考材料 → 可直接发布的课程正文（口语化、工程视角、无 AI 味） |
| [skills/course-scraper](skills/course-scraper/SKILL.md) | 课程抓取 & 双语翻译：登录在线课程平台，抓取所有课时存为 Markdown，翻译成中英对照格式 |
| [skills/content-creator](skills/content-creator/SKILL.md) | 长文 / 短视频 / 小红书等工作流（含 A/B/C/D/E/F 六条分支） |
| [skills/kangjian-skill](skills/kangjian-skill/SKILL.md) | 以康健本人风格创作公众号文章 / 短视频口播 / AI 编程教程 / 演讲稿（去 AI 味门禁） |
| [skills/web-slide](skills/web-slide/SKILL.md) | 生成可交互单文件 HTML 演讲稿：键盘翻页、演讲者备注、全局索引、代码高亮、PDF 导出 |
| [skills/ai-daily-brief](skills/ai-daily-brief/SKILL.md) | 每日 AI 情报日报（X 账号采集 + 评分 rubric） |
| [skills/daily-ai-digest](skills/daily-ai-digest/SKILL.md) | 每日 AI 前沿日报（WebSearch 采集 + P0/P1/P2 分级 + 网站自动发布） |
| [skills/weekly-report](skills/weekly-report/SKILL.md) | AI 编程周报多格式输出 |
| [skills/wiki-doc-sink](skills/wiki-doc-sink/SKILL.md) | 讨论沉淀到个人 Wiki（含 `references/` 路由说明，需配置 `<WIKI_ROOT>`） |
| [skills/markdown-format](skills/markdown-format/SKILL.md) | Pandoc/Word 稿 Markdown 格式化（Obsidian 表格、代码块、标题） |
| [skills/git-push](skills/git-push/SKILL.md) | 一键 add / 生成 commit / push（Conventional Commits + 安全约束） |

## Skills 协作关系

各 skill 不是孤立的，围绕「AI 编程内容稳定输出」形成两条主流水线。

### 主流水线 A：动态/想法 → 发布

```
daily-ai-digest / ai-daily-brief
        ↓ 素材
ai-programming-topic-planner
        ↓ 角度 + 推荐工作流
content-creator（工作流 B/C/D/F）
        ↓ 初稿
kangjian-skill（风格润色）
        ↓
    发布（公众号 / 短视频 / 小红书）
```

**典型场景**：看到 Claude Code 更新了某功能 → 用 `ai-programming-topic-planner` 找「程序员最关心的切入角度」→ 用 `content-creator` 工作流 B 孵化成文章 → 用 `kangjian-skill` 去 AI 味润色 → 发布。

---

### 主流水线 B：实战记录 → 教程 → 发布

```
一段实战记录（命令/报错/截图/过程）
        ↓
coding-session-to-tutorial
        ↓ 结构化教程初稿
ai-programming-topic-planner（可选，用于确认角度/规划系列）
        ↓
content-creator（工作流 C 润色）
        ↓
kangjian-skill（风格门禁）
        ↓
    发布
```

**典型场景**：今天用 Cursor 解决了一个棘手问题 → 把过程记录（命令+思路+弯路）交给 `coding-session-to-tutorial` 生成教程初稿 → 用 `content-creator` 工作流 C 提升叙事质量 → 用 `kangjian-skill` 确保有人味 → 发布。

---

### 各 Skill 在流水线中的定位

| Skill | 定位 | 接什么 | 输出给什么 |
|-------|------|--------|-----------|
| `daily-ai-digest` / `ai-daily-brief` | 素材来源 | — | `ai-programming-topic-planner` |
| `ai-programming-topic-planner` | 选题决策 | 动态/痛点/想法/实战记录 | `content-creator` 对应工作流 |
| `coding-session-to-tutorial` | 结构化整理 | 原始实战记录 | `content-creator` 工作流 C |
| `course-scraper` | 外部课程存档 | 在线课程 URL + 账号 | `course-generator`（素材）/ `wiki-doc-sink`（沉淀） |
| `course-generator` | 课程章节生产 | 章节大纲 + 参考材料 | `kangjian-skill` / 直接发布 |
| `content-creator` | 内容生产 | 角度/素材/初稿 | `kangjian-skill` |
| `kangjian-skill` | 风格门禁 | 任意初稿 | 发布 |
| `web-slide` | 演讲稿生成 | 主题/大纲/文档 | 独立发布（HTML） |
| `weekly-report` | 定期汇总 | 周内动态 | 独立发布 |
| `wiki-doc-sink` | 知识沉淀 | 讨论结论 | 个人 Wiki |
| `git-push` | 工程辅助 | 代码变更 | 远程仓库 |

---

## wiki-doc-sink：配置 `WIKI_ROOT`（使用前必读）

[`wiki-doc-sink`](skills/wiki-doc-sink/SKILL.md) 会把讨论沉淀到你**个人的 LLM Wiki 仓库**，而不是当前打开项���的 `docs/`。skill 内用占位符 `<WIKI_ROOT>` 表示 Wiki 根目录——**安装插件不会自动替你填路径**，需要你在本机先声明一次。

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

两条路径都能读到，再 **@ wiki-doc-sink** 或说「沉���到文档」。

### 未设置 `WIKI_ROOT` 时

若已 @ `wiki-doc-sink` 或触发「沉淀到文档」，但 Agent 不知道 Wiki 根目录：

1. **先停止写入**当前项目的 `docs/`、`README` 等默认落点（除非你在同一句里明确指定「就写在本仓库某路径」）。
2. 按上一节完成 `WIKI_ROOT` 配置，并确认 `SCHEMA.md` / `CLAUDE.md` 可读���
3. 重新发起沉淀请求；Agent 应按 Wiki 规范写入 `wiki/`，且 **`raw/` 只读**。

更完整的流程与约束见 [skills/wiki-doc-sink/SKILL.md](skills/wiki-doc-sink/SKILL.md) 与同目录 `references/`。

若你同时维护**组织/公司业务 Wiki**（例如信贷前端专用库），公司库路由请保留在本机 `~/.claude/rules/`，本仓库 skill 仅覆盖个人 `<WIKI_ROOT>`。

## Claude Code：Marketplace 安装（推荐）

将下列 `chengkj99/kj-skills` 换成你 fork 后的 `owner/repo`，并同步修改 `.claude-plugin/marketplace.json` 里 `plugins[0].source.repo`（否则 marketplace 仍指向原仓库）：

```text
/plugin marketplace add chengkj99/kj-skills
/plugin install kj-skills@kj-agent-skills
```

若 marketplace 克隆走 SSH 报错，可改用 HTTPS 添加源：

```text
/plugin marketplace add https://github.com/chengkj99/kj-skills.git
/plugin install kj-skills@kj-agent-skills
```

安装后可使用插件命令 **`/kj-help`** 快速查看各 skill 路径。

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
