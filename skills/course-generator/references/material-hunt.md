# 主动搜料策略（material-hunt）

> 好课程的底气是充足的材料，而不是 AI 自己编的「通用知识」。
> 本文件定义：搜什么、怎么搜、搜到什么算够、搜不到怎么办。

## 搜索优先级

```
官方文档 > 一手实战记录 > 高质量技术博客 > 本地已沉淀知识 > 通用知识兜底
```

- **官方文档**：准确性最高，变化跟版本走，必须抓。
- **一手实战记录**：本地 kj-skills、kj-llm-wiki 里已沉淀的真实操作经验，最贴近康健的语感。
- **高质量技术博客**：Changelog、官方 Blog、知名开发者写的深度文章。
- **通用知识兜底**：仅在以上都没覆盖时使用，且写进正文时必须保守表述，不硬写不确定的细节。

---

## 第一轮：本地仓库搜索

### 关键词提取

从章节标题提取 2–4 个核心概念，分别准备**中文**和**英文**版本。

示例：章节「Claude Code 的 Agent 模式详解」→ 关键词：
- `agent mode`、`Agent 模式`
- `claude code`、`Claude Code`
- `agentic`、`autonomous`

### 搜索路径与命令

```bash
# 1. 当前课程仓库（可能已有相关章节草稿或笔记）
grep -r "关键词" . --include="*.md" -l 2>/dev/null

# 2. kj-skills（技能文档、已有教程片段）
grep -r "关键词" /Users/chengkangjian/work/kj-skills --include="*.md" -l 2>/dev/null

# 3. kj-llm-wiki（知识沉淀、分析文章）
grep -r "关键词" "/Users/chengkangjian/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki" --include="*.md" -l 2>/dev/null

# 4. kangjian-ai-hub（历史调研和公众号文章）
grep -r "关键词" /Users/chengkangjian/work/kangjian-ai-hub --include="*.md" -l 2>/dev/null

# 5. auto-content-platform（如章节涉及内容生产相关工具）
grep -r "关键词" /Users/chengkangjian/work/auto-content-platform --include="*.md" -l 2>/dev/null

```

命中文件后：用 Read 读取，**只提取与本章相关的知识点**，不要把整个文件塞进上下文。

### 本地搜索的质量判断

| 命中内容 | 处理方式 |
|---|---|
| 完整的操作步骤 / 配置示例 | 作为「可复现段落」的核心材料 |
| 踩坑记录 / 真实经验 | 作为「常见坑」段落的素材 |
| 对比分析 / 选型建议 | 作为「怎么选 / 什么时候用」的依据 |
| 过时或不确定的内容 | 标注「待核实」，不直接引用，转网络搜索核实 |

---

## 第二轮：网络搜索

### 必搜：官方文档

根据章节涉及的工具 / 产品，**直接用 WebSearch 搜官方文档**：

| 工具 | 优先搜索目标 |
|---|---|
| Claude Code | `site:docs.anthropic.com claude code <功能关键词>` |
| Cursor | `site:docs.cursor.com <功能关键词>` |
| GitHub Copilot | `site:docs.github.com copilot <功能关键词>` |
| Codex | `site:platform.openai.com/docs/guides/codex <功能关键词>` |
| MCP | `site:modelcontextprotocol.io <关键词>` |
| 通用 AI 编程 | `<工具名> <功能> official documentation` |

用 WebFetch 抓取命中的官方文档页面，提取：
- 功能定义 / 能力边界
- 配置参数 / API 签名
- 官方示例代码
- 已知限制 / 注意事项

### 补搜：深度实战内容

官方文档搜完后，补搜 1–2 轮实战类内容：

**搜索词模板**（组合使用，选 2–3 个）：
- `<功能名> tutorial 2024` / `<功能名> tutorial 2025`
- `<功能名> best practices`
- `<功能名> vs <相近功能>` （用于写对比段落）
- `<功能名> pitfalls` / `<功能名> common mistakes`
- `<功能名> example` / `<功能名> demo`

**判断是否值得 WebFetch**（看搜索结果摘要）：
- ✅ 有具体操作步骤、代码示例、配置片段
- ✅ 来自知名开发者 / 官方 Blog / Changelog
- ✅ 发布时间在近 12 个月内（技术类内容很快过时）
- ❌ 纯理论文章、没有可操作内容 → 跳过
- ❌ SEO 堆砌、内容浅薄 → 跳过
- ❌ 链接指向论坛帖子或问答（StackOverflow 除外，具体问题具体看）→ 视摘要质量决定

每轮 WebSearch 最多抓取 3–4 个 URL，够用就不堆材料。

### 搜几轮算够

不是越多越好。以「能覆盖章节主干知识点」为标准：

- **概念讲解型**：1 篇官方文档 + 1–2 篇实战文章，通常够了。
- **工具操作型**：官方文档（必须）+ 1 篇踩坑 / 排错文章。
- **实战项目型**：官方文档 + 类似项目的完整示例代码 + 1 篇踩坑。
- **方法论型**：2–3 篇有观点的深度文章，不需要官方文档。

搜到 5–8 篇高质量材料后，停止搜索，进入「第 1 步：吃透材料」。

---

## 搜不到怎么办

| 场景 | 处理 |
|---|---|
| 官方文档有，但内容太新（知识截止日期之后） | 诚实说「基于官方文档 X 版写的，建议核实最新版行为」 |
| 某功能文档极少，只有官方简介 | 保守写，只写有把握的部分；标注「建议补充实际测试截图」 |
| 搜了 3 轮还是没有可复现示例 | 告知用户：「这个知识点缺少可复现材料，正文会有操作框架但无法给出可直接跑的代码，建议补充」 |
| 本地和网络都没有 | **不硬编**。告知用户，建议提供官方文档链接或自己跑一遍后把输出贴给我 |

---

## 材料清单格式（内部使用）

搜完后在草稿区（不输出给用户）整理：

```
【材料清单】
- [本地] kj-llm-wiki/xxx.md → 覆盖知识点：Agent 工作流原理
- [官方] docs.anthropic.com/xxx → 覆盖知识点：--dangerously-skip-permissions 参数说明
- [博客] blog.xxx.com/xxx → 覆盖知识点：Agent 模式 vs Edit 模式对比
【仍缺材料的知识点】
- 真实项目中 Agent 模式失败案例（保守处理 / 告知用户）
```

整理完就进入第 1 步，不需要把清单展示给用户（除非用户追问）。
