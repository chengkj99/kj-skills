---
name: markdown-format
description: >-
  将 Pandoc/Word 导出的 Markdown 或杂乱 GFM 整理为 Obsidian 友好格式：标题层级、GFM 表格分隔行、
  引用块提示框、围栏代码块与缩进、列表与编号修复。在用户要求「格式化 Markdown」「优化 md 可读性」、
  Obsidian 表格不显示、或处理 raw/papers 与 docx 转换稿时使用；不默认删减正文，删改须用户确认。
disable-model-invocation: true
---

# Markdown 格式化（Obsidian / GFM）

## 适用场景

- `pandoc` / Word / 语雀 导出的 `.md`（残留 HTML 表格、`**伪标题**`、逐行 `>` 代码）
- Obsidian 中 `| 列 |` 未渲染为表格（缺分隔行）
- 用户要求「格式化优化、更易阅读」，且明确**不要随意删减内容**

## 硬性约束

1. **不擅自删减正文**；若发现重复段落、冗余图片、过时章节，先列出建议，等用户确认后再删。
2. 保留文首 YAML frontmatter（`---` … `---`）与原有 wikilink、相对路径图片。
3. 用户指定只改某节时，仅改该范围。

## 推荐工作流

```text
1. Read 通读目标文件，判断来源（Pandoc / 手写 / 混合）
2. 优先运行脚本（若可写盘）：python scripts/format_markdown.py <file.md>
3. 人工扫一遍：提示框、编号、误标语言、需用户确认的重复内容
4. 在 Obsidian 预览中验证表格与代码块
```

有 Shell 权限时，在 skill 目录或仓库根执行：

```bash
python skills/markdown-format/scripts/format_markdown.py path/to/doc.md
# 预览不写盘：
python skills/markdown-format/scripts/format_markdown.py path/to/doc.md --check
```

脚本不覆盖所有语义问题；**第 3 步人工检查不可省略**。

## 转换规则（核心）

### 1. 标题

| 原文模式 | 目标 |
|----------|------|
| `**第X章 标题**` | `# 第X章 标题` |
| `**N.M 小节**` | `## N.M 小节` |
| `**macOS / …**` 等平台小标题 | `### …` |
| `**❌ 错误名**` | `### ❌ 错误名` |

文档主标题：文首 `# 主标题` + `## 副标题`；避免全文仅用加粗当标题（Obsidian 大纲失效）。

### 2. GFM 表格（Obsidian 必检）

**表头下一行必须是分隔行**，列数与表头一致：

```markdown
| **列 A** | **列 B** |
| --- | --- |
| 数据 1 | 数据 2 |
```

常见事故：清理 Pandoc 空行时误删 `|----|----|`。修复：在首个表头行后插入 `| --- | --- |`（列数 N 则 N 个 `---`）。

宽表、提示性色块表：可改为 **引用块** 或保留 GFM，勿留裸 HTML `<table>`。

### 3. 提示框（原 Word 色块 / 单列表格）

转为引用块，标题加粗：

```markdown
> **核心认知**
>
> 正文段落。多段之间用 `>` 空行分隔。
```

目录式列表放在同一引用块内时，**列表项之间不要插空行**（否则 Obsidian 断块）。

### 4. 代码块

| 内容类型 | 围栏语言 |
|----------|----------|
| Shell / `claude` / 安装命令 | `bash` |
| `settings.json` / Hooks | `json`（2 空格缩进） |
| `CLAUDE.md` / Subagent 模板 | `markdown` |
| `SKILL.md` frontmatter 示例 | `yaml` |
| 目录树 | `text` |

操作要点：

- 合并连续 `>` 引号为单个围栏块；去掉 `\|`、`\_` 等 Pandoc 转义（表内 `\[` 除外时需还原为 `[`）。
- 多行 **Claude 提示**（以 `>` 开头）：续行若无 `>`，补上 `> ` 前缀。
- JSON 用 `json.dumps(..., indent=2)` 或等价格式化；**不要把 JSON 标成 bash**。

### 5. 列表与编号

- 去掉列表项之间的多余空行。
- Word 遗留错误编号（如 7.1 节出现 5–8、特性循环 9–14）：按阅读顺序改为 1–n，**不改文字**。

### 6. 图片与页脚

- 同一二维码/配图：**HTML `<img>` + Markdown `![]()` 重复**时，保留一种（优先 Markdown 相对路径）。
- 用户要求精简页脚（如仅保留公众号）时，只改指定区块，不动正文章节。

## 完成前自检

见 [references/checklist.md](references/checklist.md)。至少确认：

- [ ] 每个表格表头后都有 `| --- | … |`
- [ ] 无未闭合的 ` ``` `、无整段裸 HTML 表
- [ ] 章节在 Obsidian 大纲中可见（`#` / `##`）
- [ ] 未删除用户未确认的内容

## 示例

Before/After 见 [examples.md](examples.md)。

## 与本仓库其他 skill 的关系

- 格式化 **`raw/` 内已有文件**：若目标仓库为 LLM Wiki，须遵守该仓 `CLAUDE.md` 对 `raw/` 只读约定；**仅在用户明确授权**时改 `raw/`。
- 格式化 **`wiki/`**：优先 Ingest 流程产出的页面；可配合 `wiki-doc-sink` / 项目内 `llm-wiki-ingest`。
