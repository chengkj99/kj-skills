---
name: wiki-doc-sink
description: >-
  将「沉淀到文档/知识库」类需求落到个人 LLM Wiki（非当前项目 docs），遵守 SCHEMA 与 raw 只读等约束。
  在用户显式 @ 本 skill、或说出「沉淀到文档」「沉淀到知识库」「沉淀内容到文档」「个人 wiki」「kj-llm-wiki」等同义语且意图为个人 Wiki 时使用；
  若用户明确指定「写在当前仓库 / 某路径」则按用户指定落点执行。
  组织/公司业务专用 Wiki 不在本 skill 范围内。
disable-model-invocation: false
---

# Wiki 文档沉淀（个人知识库）

## 范围边界

- **本 skill 仅处理个人** `<WIKI_ROOT>`，不处理组织/公司业务专用 Wiki。
- 若用户要沉淀的是业务域 Wiki，停止并按其本机已配置的业务 Wiki 规则执行（常见位置：`~/.claude/rules/`）。

## Fork 与路径配置（必读）

本 skill 的**知识库根目录**须由你自行指定（下称 `<WIKI_ROOT>`）。将下文所有 `<WIKI_ROOT>` 替换为你的 Wiki 仓库在本机的绝对路径。

维护者示例曾使用路径 `.../kj-llm-wiki`；开源使用者请改为自己的目录。

## 执行前必读（按顺序 Read）

1. 本 skill 目录下：
   - `references/personal-wiki-bridge.md`
   - `references/routing-notes.md`
2. 用户环境（若存在）：
   - `~/.claude/CLAUDE.md`（全局 `WIKI_ROOT` 等）
3. Wiki 仓库（**以磁盘为准**）：
   - `<WIKI_ROOT>/SCHEMA.md`
   - `<WIKI_ROOT>/CLAUDE.md`

## 何时写入 Wiki（默认）

当对话出现以下或**同义表述**，且意图为**个人知识库 / Wiki**（不是当前项目的 README、不是用户明确说的「就写在这个 repo」）时：

- 「沉淀内容到文档」
- 「沉淀到文档」「沉淀到知识库」
- 「把内容沉淀成文档」
- 「个人 wiki」「个人知识库」
- 其他明确表达「要把当前讨论/结论写成可长期维护的文档」且指向**个人 Wiki**

**默认应执行**：按 **`<WIKI_ROOT>`** 仓库规范写入知识库，**不要**默认写当前打开项目的 `docs/` 或随意新建说明文件。

落点含糊时，按 `references/routing-notes.md` **先问一句**（个人 Wiki vs 当前项目 `docs/`）。

## 何时写入当前项目

仅当用户**同时或随后明确指定**例如：「写在当前项目」「放在本仓库 `docs/...`」「只更新 README」等——按用户**最后一次明确指定的落点**执行。

## 查询流程（检索个人 Wiki 时）

1. 读取 `<WIKI_ROOT>/wiki/index.md` 定位条目。
2. 打开对应 `wiki/concepts/`、`wiki/analysis/`、`wiki/synthesis/` 等页面。
3. 综合多页作答；可用 `[[wiki-link]]` 标明关联。
4. **不要**修改 `raw/`（例外以 `<WIKI_ROOT>/CLAUDE.md` 为准）。

## 知识库根目录与必读规范

| 路径 | 用途 |
|------|------|
| `<WIKI_ROOT>/` | 个人 LLM Wiki 仓库根目录 |
| `<WIKI_ROOT>/SCHEMA.md` | 目录结构、页面格式、raw/wiki 边界 |
| `<WIKI_ROOT>/CLAUDE.md` | Ingest / Analysis / Synthesis / Query / Lint 步骤与硬性约束 |

## 执行要点（摘要）

1. **`raw/` 只读**：不得擅自编辑、删除、移动 `raw/` 内已有文件；例外以该仓库 `CLAUDE.md` 与 `.cursor/rules/` 为准。
2. **可写主战场为 `wiki/`**：按素材类型在 `wiki/sources/`、`wiki/concepts/`、`wiki/entities/`、`wiki/analysis/`、`wiki/synthesis/` 等路径创建或更新页面，格式遵循 `SCHEMA.md`。
3. **索引与日志**：新建或重要更新后，按需更新 `wiki/index.md`；在 `wiki/log.md` **仅追加**记录。
4. **语言与日期**：摘要与解析以中文为主；日期使用用户环境中的当前日期，不臆造。

## 对 Agent 的操作顺序（写入）

1. Read `references/` 两篇 + `SCHEMA.md` + `CLAUDE.md`，确定页面类型与路径命名。
2. 在 `wiki/` 下创建或更新页面；不触碰 `raw/` 除非该仓库规则允许。
3. 按需更新 `wiki/index.md`；向 `wiki/log.md` **追加**一行说明。
4. 若用户其实要的是项目内文档，停止并按用户指定路径写入。
5. **写入后在回复中注明**：实际写入的绝对路径与库名（个人 Wiki），便于用户核对。

## 显式使用方式

用户在 Cursor / Claude Code 中 **@ 引用本 skill**（或对话里写「按 wiki-doc-sink」）即视为启用本流程；无需依赖模型自动猜测。

## 交付前自检

- [ ] 确认动笔前已按顺序读取 `references/personal-wiki-bridge.md`、`references/routing-notes.md`、`<WIKI_ROOT>/SCHEMA.md`、`<WIKI_ROOT>/CLAUDE.md`。
- [ ] 检查页面落在 `wiki/` 下正确子目录（`sources/`、`concepts/`、`entities/`、`analysis/`、`synthesis/` 等），页面格式符合 `SCHEMA.md`。
- [ ] 在 `<WIKI_ROOT>` 运行 `git status`，确认 `raw/` 内没有任何既有文件被修改、删除或移动。
- [ ] 确认新建或重要更新已同步 `wiki/index.md`，且 `wiki/log.md` 末尾追加了一行记录、未改动既有行。
- [ ] 核对页面日期为用户环境当前日期、摘要与解析以中文为主，且回复中已注明实际写入的绝对路径与库名（个人 Wiki）。
