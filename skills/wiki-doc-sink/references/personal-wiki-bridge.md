# 个人 LLM Wiki 桥接说明

> 本文件供 `wiki-doc-sink` 执行前 **Read** 加载。路径占位符 `<WIKI_ROOT>` 须替换为你的个人 Wiki 仓库根目录。

## 何时使用个人 Wiki

- 个人学习、工程通用、AI 协作方法论、时间管理、跨项目可复用经验
- 用户明确提到「个人 wiki」「个人知识库」或自己的 Wiki 仓库名
- 内容 **不属于** 你所在组织的**业务域专用** Wiki（此类需求见 `routing-notes.md`）

## 查询流程

1. 读取 `<WIKI_ROOT>/wiki/index.md` 定位条目。
2. 打开对应 `wiki/concepts/`、`wiki/analysis/`、`wiki/synthesis/`、`wiki/sources/`、`wiki/entities/` 等页面。
3. 综合多页内容作答；答案中可用 `[[wiki-link]]` 标明概念关联（与 Obsidian 兼容）。
4. 规范与摄入流程见 `<WIKI_ROOT>/CLAUDE.md`、`<WIKI_ROOT>/SCHEMA.md`。

## 运维与工程类示例（非业务域）

常见个人库条目类型示例（实际以你的 `wiki/index.md` 为准）：

- SPA/HTTPS 排查、SSH 公钥认证、Nginx 多子域共存等工程通用模式
- AI Native、个人成长、协作纪要等可跨项目复用的方法论

## 原始数据与规范

- 不可变原始文档：`<WIKI_ROOT>/raw/`（默认只读，例外以该仓库 `CLAUDE.md` 为准）
- 全局规范：`<WIKI_ROOT>/SCHEMA.md`、`<WIKI_ROOT>/CLAUDE.md`

---

<!-- 维护者示例（fork 后可删或改为你自己的路径）：

WIKI_ROOT 示例: /Users/you/ai_space/kj-llm-wiki

-->
