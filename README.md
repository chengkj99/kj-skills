# kj-skills

Claude / Cursor / Codex **Agent Skills** 集合：AI 编程内容创作全链路、现象洞察、个人 Wiki 沉淀、课程生产、增长复盘、付费内容质检、AI 日报、周报、Git 提交推送。

## 包含的 Skills

| 目录 | 说明 |
|------|------|
| [skills/ai-programming-topic-planner](skills/ai-programming-topic-planner/SKILL.md) | AI 编程内容选题策略：输入动态/痛点/想法，输出 3-5 个内容角度 + 推荐工作流 |
| [skills/ai-learning-loop](skills/ai-learning-loop/SKILL.md) | AI 学习闭环：从主题/材料出发，生成真实问题、最小调研包、表达卡片、评审反馈和补卡决策 |
| [skills/coding-session-to-tutorial](skills/coding-session-to-tutorial/SKILL.md) | 实战记录转教程：原始命令/报错/过程 → 结构化 AI 编程教程初稿 |
| [skills/course-generator](skills/course-generator/SKILL.md) | 单章节课程正文生成：章节大纲 + 参考材料 → 可直接发布的课程正文（口语化、工程视角、无 AI 味）；写完后自动为 `[流程图]`/`[对比图]` 生成 SVG 插图 |
| [skills/course-campaign](skills/course-campaign/SKILL.md) | 批量章节编排（工头）：按清单逐章调用 course-generator，负责顺序管理、上下文衔接、进度持久化、里程碑 compact、收尾图片规范化审计 |
| [skills/content-illustrator](skills/content-illustrator/SKILL.md) | 内容插图工具（三模式）：① 文字描述 → SVG；② 分析文章识别「看图比看字快」的位置并自动生成插图；③ 批量补全课程文件中的 `[流程图]`/`[对比图]` 占位符 |
| [skills/course-scraper](skills/course-scraper/SKILL.md) | 课程抓取 & 双语翻译：登录在线课程平台，抓取所有课时存为 Markdown，翻译成中英对照格式 |
| [skills/content-creator](skills/content-creator/SKILL.md) | 长文 / 短视频 / 小红书等工作流（含 A/B/C/D/E/F 六条分支） |
| [skills/phenomenon-insight](skills/phenomenon-insight/SKILL.md) | 现象本质洞察：把真实事件/困惑拆成隐含假设、机制、反常识判断和内容观点 |
| [skills/local-stt-transcription](skills/local-stt-transcription/SKILL.md) | 本地视频/音频转最终校对文字稿：调用 jianchang512/stt，默认 medium + 术语校对润色，高精度 large-v3 + 校对 |
| [skills/kangjian-skill](skills/kangjian-skill/SKILL.md) | 以康健本人风格创作公众号文章 / 短视频口播 / AI 编程教程 / 演讲稿（去 AI 味门禁） |
| [skills/tutorial-guide](skills/tutorial-guide/SKILL.md) | 新手教程指南生成：主题 / 链接 → Markdown + Word `.docx` 完整指南（含封面、目录、引流页） |
| [skills/wechat-companion](skills/wechat-companion/SKILL.md) | 公众号发布配套物料：前言、标题、摘要、封面图提示词、朋友圈和社群转发文案 |
| [skills/wechat-publish-kit](skills/wechat-publish-kit/SKILL.md) | 公众号发布包：正文 → 配套文案、封面图/提示词、发布用 Markdown、结构优化与可选草稿发布 |
| [skills/web-slide](skills/web-slide/SKILL.md) | 生成可交互单文件 HTML 演讲稿：键盘翻页、演讲者备注、全局索引、代码高亮、PDF 导出 |
| [skills/knowledge-map](skills/knowledge-map/SKILL.md) | 知识地图生成：输入一个主题 → 先做 3-5 轮调研，再输出高信息密度的单文件 HTML 信息图（深色卡片网格、阶段流程条、实战工作流，可截图为长图/海报） |
| [skills/ai-daily-from-x](skills/ai-daily-from-x/SKILL.md) | 每日 AI 情报日报（X 账号采集 + 评分 rubric） |
| [skills/ai-daily-websearch](skills/ai-daily-websearch/SKILL.md) | 每日 AI 前沿日报（WebSearch 采集 + P0/P1/P2 分级 + 网站自动发布） |
| [skills/ai-coding-weekly-report](skills/ai-coding-weekly-report/SKILL.md) | AI 编程中文周报：采集、筛选、中文摘要、价值影响判断和引用链接 |
| [skills/kangjian-douyin-media](skills/kangjian-douyin-media/SKILL.md) | 程序员康健抖音数据增量抓取、归档与评论/作品 Markdown 报告生成 |
| [skills/content-growth-review](skills/content-growth-review/SKILL.md) | 内容增长复盘：基于抖音/视频号/公众号/小红书数据诊断问题、调整方向、生成选题池 |
| [skills/paid-content-review](skills/paid-content-review/SKILL.md) | 付费课程 / 专栏 / 文章上线前质检：按 P0/P1/P2 输出结构、准确性、付费价值审查报告 |
| [skills/weekly-digest](skills/weekly-digest/SKILL.md) | Git 周报生成器：从单项目或多项目 git log 生成结构化中文周报 |
| [skills/skills-repo-health-check](skills/skills-repo-health-check/SKILL.md) | Skills 仓库健康度检查：按结构、触发、验证、索引、去重、安全等维度审计并给出迭代计划 |
| [skills/wiki-doc-sink](skills/wiki-doc-sink/SKILL.md) | 讨论沉淀到个人 Wiki（含 `references/` 路由说明，需配置 `<WIKI_ROOT>`） |
| [skills/markdown-format](skills/markdown-format/SKILL.md) | Pandoc/Word 稿 Markdown 格式化（Obsidian 表格、代码块、标题） |
| [skills/git-push](skills/git-push/SKILL.md) | 一键 add / 生成 commit / push（Conventional Commits + 安全约束） |
| [skills/wiki-intelligence](skills/wiki-intelligence/SKILL.md) | Claude Code hook 系统：提示词质量评分、好提示词自动收藏、对话价值分析与知识沉淀引导（详见 [docs/wiki-intelligence.md](docs/wiki-intelligence.md)） |

## wiki-intelligence Hook 结构

`wiki-intelligence` 由「Claude Code 事件入口脚本」和「共享函数库」两层组成：前者由 Claude Code 在固定时机直接调用，后者被入口脚本 `source` 后复用。

```text
Claude Code 事件
├── SessionStart
│   └── ~/.claude/hooks/session-start-cleanup.sh
│       └── source lib/wiki-intelligence.sh
│           ├── wi_load_config()
│           └── wi_cleanup_stale_state()
│               └── 清理 ~/.claude/state/wiki-intelligence/session-*.json
├── UserPromptSubmit
│   └── ~/.claude/hooks/prompt-quality.sh
│       ├── source lib/wiki-intelligence.sh
│       │   ├── wi_load_config()
│       │   ├── wi_is_high_value_intent()
│       │   └── wi_analyze_prompt()
│       └── source lib/wiki-writer.sh
│           └── ww_save_good_prompt()
└── Stop
    └── ~/.claude/hooks/knowledge-capture.sh
        ├── source lib/wiki-intelligence.sh
        │   ├── wi_load_config()
        │   └── wi_analyze_knowledge()
        └── source lib/wiki-writer.sh
            └── ww_write_session_bullets()
```

源码位于 `skills/wiki-intelligence/hooks/`：

| 类型 | 文件 | 作用 |
|------|------|------|
| 事件入口 | `prompt-quality.sh` | `UserPromptSubmit` 时运行，检查提示词质量，必要时收藏好提示词 |
| 事件入口 | `knowledge-capture.sh` | `Stop` 时运行，分析对话价值并写入沉淀提示状态 |
| 事件入口 | `session-start-cleanup.sh` | `SessionStart` 时运行，清理超过 24 小时的 `~/.claude/state/wiki-intelligence/session-*.json` 状态文件 |
| 共享库 | `lib/wiki-intelligence.sh` | 配置加载、意图识别、AI 分析、状态清理等核心能力 |
| 共享库 | `lib/wiki-writer.sh` | 写入好提示词、更新 session bullets 等文件写入能力 |

安装脚本会把入口脚本和 `lib/` 一起复制到 `~/.claude/hooks/`，并在 `~/.claude/settings.json` 中注册 `SessionStart`、`UserPromptSubmit`、`Stop` 三个事件。注意：`lib/*.sh` 不会被 Claude Code 直接调用，它们只是入口脚本内部复用的工具箱；运行状态放在 `~/.claude/state/wiki-intelligence/` 下，避免和其他 Claude 工具共用 `~/.claude/state` 根目录。

## Skills 协作关系

各 skill 不是孤立的，围绕「学习输入 -> 知识沉淀 -> 内容稳定输出」形成三条主流水线，并补充课程生产、发布配套和质量审查能力。

### 主流水线 0：学习目标 / 材料 → 表达卡片 → 知识沉淀

```
学习主题 / 外部材料 / 临时想法
        ↓
ai-learning-loop
        ↓ 真实问题 + 最小调研包 + 表达卡片
内置输出评审步骤
        ↓ 补卡建议
wiki-doc-sink（需要沉淀时）
        ↓
个人 Wiki / topic-bank / studio 内容生产轨
```

**典型场景**：想学习一个主题但没有资料 → 用 `ai-learning-loop` 先收敛真实问题和最小阅读包 → 产出一张口播/短文表达卡片 → 评审盲区 → 只补一张必要的 `concepts` 或 `playbooks` 卡片。

---

### 主流水线 A：动态/想法 → 发布

```
ai-daily-websearch / ai-daily-from-x
        ↓ 素材
ai-programming-topic-planner
        ↓ 角度 + 推荐工作流
phenomenon-insight（可选，深挖机制/反常识）
        ↓ 核心洞见 + 内容入口
content-creator（工作流 B/C/D/F）
        ↓ 初稿
kangjian-skill（风格润色）
        ↓
    发布（公众号 / 短视频 / 小红书）
```

短视频原始素材可先经过：

```
本地视频/音频
        ↓
local-stt-transcription（medium/large-v3 + 术语校对）
        ↓ 已发布内容的最终校对文字稿
raw/studio/transcripts（已发布短视频内容资产）
        ↓ 连载选题规划：系列主题 / 下一集角度 / 未展开分支
content-creator / kangjian-skill
        ↓
    发布（短视频 / 公众号 / 小红书）
```

**典型场景**：看到 Claude Code 更新了某功能 → 用 `ai-programming-topic-planner` 找「程序员最关心的切入角度」→ 用 `phenomenon-insight` 把现象拆到机制和反常识判断 → 用 `content-creator` 工作流 B 孵化成文章 → 用 `kangjian-skill` 去 AI 味润色 → 发布。

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

### 主流水线 C：发布数据 → 增长复盘 → 下一轮选题

```
抖音 / 视频号 / 公众号 / 小红书发布数据
        ↓
kangjian-douyin-media（抖音增量抓取与归档）
        ↓
content-growth-review（增长诊断 + 评论洞察 + 方向调整）
        ↓
raw/studio/funnel/backlog/manual（选题池）
        ↓
content-creator / kangjian-skill
        ↓
    下一轮发布
```

**典型场景**：抖音发布了一批 AI 编程短视频 → 用 `kangjian-douyin-media` 更新作品和评论归档 → 用 `content-growth-review` 找出涨粉弱、互动异常或值得延展的选题 → 把高价值方向沉淀到选题池。

---

### 各 Skill 在流水线中的定位

| Skill | 定位 | 接什么 | 输出给什么 |
|-------|------|--------|-----------|
| `ai-daily-websearch` / `ai-daily-from-x` | 素材来源 | — | `ai-programming-topic-planner` |
| `ai-programming-topic-planner` | 选题决策 | 动态/痛点/想法/实战记录 | `content-creator` 对应工作流 |
| `ai-learning-loop` | 学习闭环总控 | 学习主题/材料/想法 | 表达卡片、评审反馈、补卡建议 / `wiki-doc-sink` |
| `phenomenon-insight` | 洞察前置层 | 真实现象/困惑/异常反馈/生活观察 | 核心洞见、反常识判断、标题与结构入口 / `content-creator` / `kangjian-skill` |
| `coding-session-to-tutorial` | 结构化整理 | 原始实战记录 | `content-creator` 工作流 C |
| `course-scraper` | 外部课程存档 | 在线课程 URL + 账号 | `course-generator`（素材）/ `wiki-doc-sink`（沉淀） |
| `local-stt-transcription` | 本地音视频转最终校对文字稿 | `.mov` / `.mp4` / `.m4a` 等本地素材 | `raw/studio/transcripts` / `content-creator` / `kangjian-skill` |
| `course-generator` | 课程章节生产 | 章节大纲 + 参考材料 | `kangjian-skill` / 直接发布 |
| `course-campaign` | 批量课程编排 | 章节清单 / 课程计划 | `course-generator` / 图片完成度报告 |
| `content-illustrator` | 插图补全 | 描述 / 文章 / 课程占位符 | SVG 插图 / 课程正文 |
| `content-creator` | 内容生产 | 角度/素材/初稿 | `kangjian-skill` |
| `kangjian-skill` | 风格门禁 | 任意初稿 | 发布 |
| `tutorial-guide` | 新手指南生产 | 主题 / 链接 | Markdown + Word 指南 / `wechat-companion` |
| `wechat-companion` | 公众号配套物料 | 文章主题 / 摘要 / 初稿 | 标题 / 前言 / 摘要 / 封面 prompt / 转发文案 |
| `wechat-publish-kit` | 公众号发布包总控 | 正文 Markdown/Word、配套物料、封面 prompt | 发布用 Markdown / 封面图 / 公众号草稿 |
| `paid-content-review` | 付费内容质检 | 单篇 / 整课 / 发布前材料 | 审查报告 / 改稿清单 |
| `kangjian-douyin-media` | 抖音归档 | 程序员康健抖音账号数据 | `content-growth-review` |
| `content-growth-review` | 增长诊断与选题 | 平台数据 / 评论 / 作品归档 | 复盘报告 / 手动选题池 |
| `knowledge-map` | 知识地图生成 | 主题 / 领域 | 单文件 HTML 信息图 |
| `web-slide` | 演讲稿生成 | 主题/大纲/文档 | 独立发布（HTML） |
| `ai-coding-weekly-report` | 定期汇总 | 周内动态 | 独立发布 |
| `weekly-digest` | Git 周报 | 单项目或多项目 git log | 周报摘要 |
| `skills-repo-health-check` | 仓库治理审计 | skills 仓库 / 新增或迁移后的 skill 集合 | 健康度评分、P0/P1/P2 修复计划 |
| `wiki-doc-sink` | 知识沉淀 | 讨论结论 | 个人 Wiki |
| `git-push` | 工程辅助 | 代码变更 | 远程仓库 |
| `wiki-intelligence` | 知识自动化 | 高价值提示词 + 对话 | wiki 知识库 |

---

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

## 课程图片生成协议（image-protocol）

`course-generator` 和 `course-campaign` 内置了图片生成协议，让课程图文并茂不再依赖手动截图。

### 工作方式

写课程正文时，在需要放图的位置用占位注释标记：

```markdown
<!-- [流程图] 描述：三层 CLAUDE.md 加载顺序，从上到下依次叠加：① 用户级（浅蓝底）→ ② 项目根（浅绿底）→ ③ 子目录（浅橙底）；标注「三层叠加生效，下层可覆盖上层」 -->
```

`course-generator` 写完章节正文后（Step 3.5），自动扫描并处理：

| 占位类型 | 处理方式 |
|---------|---------|
| `[流程图]` | ✅ 自动生成 SVG，写入 `assets/` |
| `[对比图]` | ✅ 自动生成 SVG，写入 `assets/` |
| `[截图]` | 保留注释，录课时手动补 |
| `[录屏建议]` | 保留注释，录课时执行 |

生成后，注释与图片引用**并存**（A 方案），描述永不丢失：

```markdown
<!-- [流程图] 描述：三层 CLAUDE.md 加载顺序... -->
![CLAUDE.md 层级示意图](../../../../assets/lessons-claudecode/cc005-claudemd-hierarchy.svg)
```

### 批量写课后的图片报告（course-campaign）

`course-campaign` 全部章节完成后自动执行 Step E：

1. **E1 规范化**：将章节里 `![](*.png)` 语法的截图统一替换为 `<img width="620">` HTML 标签，确保 SVG 与 PNG 等宽一致
2. **E2 报告**：输出完成度清单，告诉你哪些截图/录屏还需要手动补充

```
📊 图片完成度报告
✅ SVG 已生成：14 张
🖼️ PNG 已规范化：3 处（统一为 width=620）
📷 截图待补：18 处
   - CC-007:37 — Plan Mode 界面截图
   ...
🎬 录屏待录：2 处
```

### SVG 风格规范

生成的 SVG 遵循统一规范（详见 [`skills/course-generator/references/image-protocol.md`](skills/course-generator/references/image-protocol.md)）：

- 画布 620×480，字体 PingFang SC / Microsoft YaHei
- 三层配色：浅蓝（`#E8F4FD`）/ 浅绿（`#EAF7EE`）/ 浅橙（`#FEF3E8`）
- 每条箭头必须有文字标注，生成后用 `open` 本地预览验证

---

## 本地 Skills 同步（`sync-claude-skills.sh`）

`~/.claude/skills/` 通过 symlink 指向本仓库的 `skills/` 子目录。**新增 skill 后**需运行一次同步脚本，让全局 Claude 立即可见：

```bash
# 全量同步
npm run sync
# 或直接运行脚本
./sync-claude-skills.sh
```

只安装某个（或某几个）skill：

```bash
npm run sync:one:claude -- content-creator
npm run sync:one:claude -- content-creator git-push course-generator
# 或直接运行脚本
./sync-claude-skills.sh content-creator git-push
```

脚本会自动扫描 `skills/` 下所有目录与 `.skill` 文件，对缺失的 symlink 进行补建，已存在的跳过不动。

> **修改已有 skill 内容**无需运行脚本，symlink 实时生效。只有**新增** skill 目录时才需要执行一次。

新增 skill 时，请同步更新本 README 的「包含的 Skills」清单；若会影响协作流程、安装方式或命令帮助，也要同步更新「Skills 协作关系」、安装说明和 `.claude/commands/kj-help.md` 等相关文档。贡献前可对照 [CONTRIBUTING.md](CONTRIBUTING.md) 的新增 skill 检查项。

## Codex：本地 Skills 注册

Codex 用户级 skills 默认位于 `~/.codex/skills/`（若设置了 `CODEX_HOME`，则为 `$CODEX_HOME/skills/`）。运行脚本可把本仓库 `skills/` 下的目录或 `.skill` 文件软链过去：

```bash
./sync-codex-skills.sh
```

只注册某几个 skill：

```bash
./sync-codex-skills.sh content-creator git-push
```

脚本会自动创建目标目录，并跳过已存在的同名条目。注册新 skill 后，重启 Codex 或开启新会话让技能列表重新加载。

---

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

## Codex：插件安装

仓库已包含 `.codex-plugin/` 清单和 `.agents/plugins/marketplace.json`，支持作为 Codex 本地插件安装。

本地克隆后，在 Codex 里添加本仓库 marketplace，然后安装插件：

```bash
codex plugin marketplace add /path/to/kj-skills
codex plugin add kj-skills@kj-agent-skills
```

本地开发期间若修改了 `.codex-plugin/plugin.json` 或新增 skill，请重新执行安装命令，并开启新会话测试。只想把 skills 直接注册到用户级目录时，用上面的 `./sync-codex-skills.sh` 即可。

## 单 skill 安装

### 不克隆仓库（推荐）

发布到 npm 后，任意机器一条命令搞定：

```bash
# 默认安装到 Claude Code
npx kj-skills install git-push

# 指定平台
npx kj-skills install git-push --for cursor
npx kj-skills install git-push --for codex
npx kj-skills install git-push --for claude
```

内部通过 `degit` 只下载该 skill 子目录，无需 clone 整个仓库。

### 已克隆仓库

只需某一目录时，按平台选一条：

| 平台 | 命令 | 目标路径 |
|------|------|---------|
| Claude Code | `npm run sync:one:claude -- <skill-name>` | `~/.claude/skills/` |
| Codex | `npm run sync:one:codex -- <skill-name>` | `~/.codex/skills/` |
| Cursor | `npm run sync:one:cursor -- <skill-name>` | `~/.cursor/skills/` |

## 许可证

MIT，见 [LICENSE](LICENSE)。
