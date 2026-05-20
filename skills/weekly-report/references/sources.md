# AI 编程周报 — 数据源清单

> 本文件定义了周报采集的所有数据源。按优先级排序，高优先级源必须采集，中/低优先级根据时间和产出量酌情采集。

---

## Tier 1：核心源（必采）

### 模型公司官方

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| OpenAI | Blog / Research / API Docs | GPT 系列更新、API 能力、Codex | `OpenAI release update coding` |
| Anthropic | News / Research / Docs | Claude 更新、AI 编程能力、MCP | `Anthropic Claude update coding MCP` |
| Google DeepMind | Blog / Research | Gemini 更新、代码能力 | `Google DeepMind Gemini coding update` |
| Meta AI (FAIR) | Blog / Research | Llama 系列、开源代码模型 | `Meta AI Llama coding open source` |

### AI IDE & 编程工具

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| Cursor | Blog / Changelog / X(@cursor_ai) | 新功能、版本更新 | `Cursor IDE update release changelog` |
| Windsurf (Codeium) | Blog / Changelog | 编辑器更新、AI 能力 | `Windsurf Codeium update release` |
| GitHub Copilot | Blog / Changelog | Copilot 更新、Agent 模式 | `GitHub Copilot update agent` |
| Claude Code | Anthropic Docs / npm | CLI 工具更新 | `Claude Code CLI update release` |
| Cline | GitHub Releases | 插件更新 | `Cline VS Code AI update` |
| Aider | GitHub Releases / Blog | CLI 工具更新 | `Aider AI coding update` |

### 开源 & 社区

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| GitHub Trending | github.com/trending | AI 编程相关热门项目 | `GitHub trending AI coding programming` |
| Hugging Face | Models / Blog | 开源代码模型、数据集 | `Hugging Face code model release` |

---

## Tier 2：重要源（应采）

### 基础设施 & 平台

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| NVIDIA | Developer Blog / GTC | 推理优化、编程加速 | `NVIDIA AI coding inference update` |
| Microsoft | Build / Azure AI Docs | Azure AI、开发者工具 | `Microsoft AI developer tools update` |
| Apple | Machine Learning / WWDC | 端侧 AI 编程能力 | `Apple machine learning developer update` |
| Vercel | Blog | v0、AI 前端工具 | `Vercel v0 AI update` |

### 学术 & 论文

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| arXiv | cs.AI / cs.SE / cs.CL | 代码生成、程序合成论文 | `arXiv code generation AI programming paper` |
| Papers with Code | 搜索 | 代码相关论文 + 实现 | `Papers with Code AI coding benchmark` |

### Agent & 框架

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| LangChain | Blog / GitHub | 框架更新 | `LangChain update release` |
| CrewAI | Blog / GitHub | 多 Agent 框架 | `CrewAI update release` |
| AutoGen | GitHub | 微软多 Agent 框架 | `AutoGen Microsoft update` |
| Devin (Cognition) | Blog | AI 软件工程师 | `Devin Cognition AI engineer update` |

---

## Tier 3：信号源（选采）

### 关键人物 X/Twitter 动态

> 这些人物的动态通常通过 manual-input.md 手动补充，因 X/Twitter 无法直接 API 采集。WebSearch 可作为辅助手段。

| 人物 | X 账号 | 关注重点 |
|------|--------|----------|
| Sam Altman | @sama | OpenAI 产品节奏、路线判断 |
| Dario Amodei | — | Claude 方向、安全对齐 |
| Andrej Karpathy | @karpathy | AI 编程实战洞察、工程直觉 |
| Yann LeCun | @ylecun | 反共识观点、研究方向 |
| Andrew Ng | — | AI 应用与学习路径 |
| Jensen Huang | — | 算力生态、GTC 信号 |

### 中文社区

| 源 | 采集入口 | 关注重点 | WebSearch 关键词 |
|----|----------|----------|-----------------|
| 即刻 | 搜索 | AI 编程中文讨论 | `即刻 AI 编程 Cursor` |
| 少数派 | 搜索 | AI 工具深度体验 | `少数派 AI 编程工具` |
| InfoQ | 搜索 | AI 工程化实践 | `InfoQ AI 编程 工程化` |

---

## 采集执行指南

1. **Tier 1 全部采集**，每个源至少执行一次 WebSearch
2. **Tier 2 按需采集**，优先采集有新版本发布的源
3. **Tier 3 作为补充**，主要依赖 manual-input.md 人工输入
4. 每个源的 WebSearch 加上时间限定（如 `after:2026-02-20`）以确保时效性
5. 对英文结果，在采集阶段即完成中文翻译
