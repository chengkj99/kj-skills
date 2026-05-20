---
name: wiki-doc-sink
description: >-
  将「沉淀到文档」类需求落到个人知识库 Wiki（非当前项目 docs），并遵守该 Wiki 的 SCHEMA 与 raw 只读等约束。
  在用户显式 @ 本 skill、或说出「沉淀到文档」「沉淀内容到文档」「把内容沉淀成文档」等同义语且意图为个人 Wiki 时使用；
  若用户明确指定「写在当前仓库 / 某路径」则按用户指定落点执行。
disable-model-invocation: true
---

# Wiki 文档沉淀（个人知识库）

## Fork 与路径配置（必读）

本 skill 的**知识库根目录**须由你自行指定（下称 `<WIKI_ROOT>`）。将下文所有 `<WIKI_ROOT>` 替换为你的 Wiki 仓库在本机的绝对路径。

维护者示例曾使用路径 `.../kj-llm-wiki`；开源使用者请改为自己的目录。

执行前应用 **Read** 核对以下文件是否已被你更新（**以磁盘为准**）：

- `~/.claude/CLAUDE.md`（若你在其中定义了全局沉淀规则）
- `<WIKI_ROOT>/SCHEMA.md`
- `<WIKI_ROOT>/CLAUDE.md`

## 何时写入 Wiki（默认）

当对话出现以下或**同义表述**，且意图为**个人知识库 / Wiki**（不是当前项目的 README、不是用户明确说的「就写在这个 repo」）时：

- 「沉淀内容到文档」
- 「沉淀到文档」
- 「把内容沉淀成文档」
- 其他明确表达「要把当前讨论/结论写成可长期维护的文档」且指向**个人 Wiki**

**默认应执行**：按 **`<WIKI_ROOT>`** 仓库规范写入知识库，**不要**默认写当前打开项目的 `docs/` 或随意新建说明文件。

## 何时写入当前项目

仅当用户**同时或随后明确指定**例如：「写在当前项目」「放在本仓库 `docs/...`」「只更新 README」等——按用户**最后一次明确指定的落点**执行。

仍有歧义时：**先简短问一句**再写入。

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

## 对 Agent 的操作顺序

1. 读取 `SCHEMA.md` + `<WIKI_ROOT>/CLAUDE.md`，确定页面类型与路径命名。
2. 在 `wiki/` 下创建或更新页面；不触碰 `raw/` 除非该仓库规则允许。
3. 按需更新 `wiki/index.md`；向 `wiki/log.md` **追加**一行说明。
4. 若用户其实要的是项目内文档，停止并按用户指定路径写入。

## 显式使用方式

用户在 Cursor / Claude Code 中 **@ 引用本 skill**（或对话里写「按 wiki-doc-sink」）即视为启用本流程；无需依赖模型自动猜测。
