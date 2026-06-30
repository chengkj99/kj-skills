# Wiki Intelligence：安装与使用指南

一套 Claude Code hook 系统，让每次对话都能为知识库自动增值——提示词评分、好提示词收藏、对话价值分析与知识沉淀引导，全程无需手动触发。

## 功能概览

| 时机 | Hook 事件 | 行为 |
|------|-----------|------|
| 发送提示词前 | `UserPromptSubmit` | 识别高价值意图 → AI 评分 → 低分给出改进建议；高分静默收藏到 wiki |
| 回答结束后 | `Stop` | 分析对话价值 → 高分输出要点摘要 → 引导「确认沉淀」 |
| 会话启动时 | `SessionStart` | 自动清理 24h 过期的会话状态文件 |

### 提示词评分维度

| 维度 | 分值 | 说明 |
|------|------|------|
| 目标清晰度 | 0–3 | 任务目标是否明确 |
| 上下文充分度 | 0–3 | 是否提供了足够背景 |
| 输出格式说明 | 0–2 | 是否说明了期望的输出形式 |
| 约束与边界 | 0–2 | 是否说明了限制条件 |

### 对话价值评分维度

| 维度 | 分值 | 说明 |
|------|------|------|
| 概念深度 | 0–3 | 是否解释了非显而易见的原理或概念 |
| 实践价值 | 0–3 | 是否包含可复用的方法、框架或决策标准 |
| 新颖性 | 0–2 | 相对于常识，是否提供了新视角 |
| 结构性 | 0–2 | 内容是否有清晰结构，便于日后检索 |

## 安装

### 前置依赖

- **jq** — JSON 解析（`brew install jq`）
- **python3** — 解析对话记录（macOS 自带）
- **claude CLI** — AI 分析子进程（Claude Code 自带）

### 安装步骤

```bash
# 1. 一键安装（复制 hooks + 注册到 settings.json）
bash skills/wiki-intelligence/install.sh
```

脚本会自动完成：

1. 将 `hooks/` 下的脚本复制到 `~/.claude/hooks/`
2. 在 `~/.claude/` 下创建配置文件（如不存在）
3. 向 `~/.claude/settings.json` 注册三个 hook

### 配置 Wiki 路径（安装后必做）

```bash
vim ~/.claude/wiki-intelligence.config.json
```

将 `wiki_path` 改为你的 wiki 仓库绝对路径：

```json
{
  "wiki_path": "/Users/didi/ai_space/kj-llm-wiki",
  ...
}
```

### 重启 Claude Code

安装和配置完成后，重启 Claude Code 使 hooks 生效。

## 配置参考

配置文件：`~/.claude/wiki-intelligence.config.json`

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `wiki_path` | *(必填)* | wiki 仓库根目录（支持 `~`） |
| `collab_notes_path` | `raw/notes/ai-collab` | 协作笔记相对路径 |
| `quality_threshold` | `7` | 提示词评分 ≥ 此值则自动收藏 |
| `knowledge_threshold` | `6` | 对话评分 ≥ 此值则提示沉淀 |
| `high_value_intents` | `["设计","分析","规划","架构","方案","design","analyze","plan","architecture","review"]` | 触发质量检查的关键词列表 |
| `analysis_model` | `claude-haiku-4-5-20251001` | 用于 AI 分析的模型（用 Haiku 控制成本） |
| `enabled` | `true` | 全局开关 |
| `prompt_check_enabled` | `true` | 提示词质量检查开关 |
| `knowledge_capture_enabled` | `true` | 知识沉淀捕获开关 |
| `prompt_collection_enabled` | `true` | 好提示词自动收藏开关 |
| `prompt_collection_path` | `wiki/playbooks/prompts` | wiki 内的提示词存储路径（相对） |
| `min_prompt_length` | `20` | 短于此字符数的提示词跳过检查 |

### 配置示例

```json
{
  "wiki_path": "/Users/didi/ai_space/kj-llm-wiki",
  "collab_notes_path": "raw/notes/ai-collab",
  "quality_threshold": 7,
  "knowledge_threshold": 6,
  "high_value_intents": ["设计", "分析", "规划", "架构", "方案", "design", "analyze", "plan", "architecture", "review"],
  "analysis_model": "claude-haiku-4-5-20251001",
  "enabled": true,
  "prompt_check_enabled": true,
  "knowledge_capture_enabled": true,
  "prompt_collection_enabled": true,
  "prompt_collection_path": "wiki/playbooks/prompts",
  "min_prompt_length": 20
}
```

## 日常使用

安装后无需手动调用，系统在三个时机自动运行：

### 1. 提示词质量检查

当你发送的提示词：

- **包含高价值关键词**（设计/分析/规划/架构/方案/design/analyze/plan/architecture/review）
- **长度 ≥ 20 字符**

hook 自动调用 AI 评分：

- **高分（≥ 7）** → 静默收藏到 `{wiki_path}/wiki/playbooks/prompts/` 下按意图分类的文件
- **低分（< 7）** → 在终端显示改进建议，格式如：
  ```
  💡 提示词建议（4/10）：缺少输出格式说明 — 请说明期望的输出形式
  ```

### 2. 对话价值分析与沉淀引导

回答结束后，如果本会话曾被标记为高价值（提示词评分通过），hook 自动分析最近 3 轮对话：

- **高分（≥ 6）** → 在终端输出要点摘要并提示沉淀：
  ```
  📖 本轮对话有沉淀价值（8/10，类型：framework）
     要点：
     • 微前端架构选型的三个关键决策点
     • Module Federation 与 qiankun 的适用场景对比
     • 渐进式迁移策略的步骤拆解
     回复「确认沉淀」将保存到 wiki，或忽略此条
  ```
- **低分** → 静默跳过，不打扰

回复「确认沉淀」后，由 Claude 侧规则处理写入（会走双知识库路由确认流程）。

### 3. 会话状态清理

每次启动新会话时，自动删除超过 24 小时的 wiki-intelligence 会话状态文件（`~/.claude/state/wiki-intelligence/session-*.json`），避免磁盘堆积，也避免误清理其他 Claude 工具放在 `~/.claude/state` 下的数据。

## 好提示词存储结构

高分提示词自动写入 `{wiki_path}/wiki/playbooks/prompts/`，按意图分类：

```
wiki/playbooks/prompts/
├── design.md      # 设计/架构类
├── analysis.md    # 分析/研究类
├── planning.md    # 规划/方案类
└── general.md     # 其他
```

每个文件中条目格式：

```markdown
### 2026-06-08 — 架构
> 帮我设计一个微前端架构方案，需要支持三个已有子应用的渐进式迁移，当前技术栈是 Vue2 + Webpack

**质量评分**：8/10
```

## 运行机制详解

### 流程图

```
用户输入提示词
    │
    ▼
[UserPromptSubmit hook]
    │
    ├─ 短于 20 字符？ → 跳过
    ├─ 不含高价值关键词？ → 跳过
    │
    ▼
调用 AI 评分（claude -p，Haiku 模型，15s 超时）
    │
    ├─ 评分 ≥ 7 → 静默收藏到 wiki → 写入会话状态文件
    └─ 评分 < 7 → 显示改进建议 → 写入会话状态文件

─────────────────────

对话结束
    │
    ▼
[Stop hook]
    │
    ├─ 会话状态文件不存在？ → 跳过
    ├─ 对话记录不存在？ → 跳过
    │
    ▼
提取最近 3 轮对话（max 3000 字符）
    │
    ▼
调用 AI 评估对话价值（20s 超时）
    │
    ├─ 评分 ≥ 6 → 输出要点摘要 + 引导沉淀
    └─ 评分 < 6 → 静默跳过

─────────────────────

新会话启动
    │
    ▼
[SessionStart hook]
    │
    ▼
清理 > 24h 的 ~/.claude/state/wiki-intelligence/session-*.json
```

### 安全设计

- **所有 hook 均以 `exit 0` 结束**，永远不会阻塞 Claude Code 正常运行
- AI 分析调用设有超时（评分 15s，对话分析 20s），超时自动放弃
- 配置文件缺失时使用合理的默认值，不会报错中断

### 日志

运行日志写入 `~/.claude/wiki-intelligence.log`，包含：

- AI 调用超时/空响应
- 好提示词收藏记录
- 配置加载异常

## 运行测试

```bash
# 快速测试（跳过需要 claude CLI 的集成测试）
WI_SKIP_CLAUDE_TESTS=1 bash skills/wiki-intelligence/tests/test-wiki-intelligence.sh

# 完整测试（在 Claude Code 外部运行，需要 claude CLI 可用）
bash skills/wiki-intelligence/tests/test-wiki-intelligence.sh
```

## 文件结构

```
skills/wiki-intelligence/
├── SKILL.md                              # Skill 元数据与简要说明
├── install.sh                            # 一键安装脚本
├── wiki-intelligence.config.example.json # 配置示例
├── hooks/
│   ├── prompt-quality.sh                 # UserPromptSubmit hook（提示词评分）
│   ├── knowledge-capture.sh              # Stop hook（对话价值分析）
│   ├── session-start-cleanup.sh          # SessionStart hook（状态清理）
│   └── lib/
│       ├── wiki-intelligence.sh          # 分析引擎（共享库）
│       └── wiki-writer.sh                # Wiki 写入工具
└── tests/
    └── test-wiki-intelligence.sh         # 测试脚本
```

## 常见问题

### Q: 安装后没有生效？

确认以下步骤：
1. 运行过 `install.sh` 且输出无报错
2. 已编辑 `~/.claude/wiki-intelligence.config.json` 设置了正确的 `wiki_path`
3. **重启了 Claude Code**

### Q: AI 分析消耗多少 token？

评分使用 `claude-haiku-4-5-20251001` 模型，每次调用输入约 200–500 token，输出约 50–100 token。只有在提示词包含高价值关键词时才会触发，日常闲聊不会调用。

### Q: 如何临时关闭？

编辑 `~/.claude/wiki-intelligence.config.json`，将 `enabled` 设为 `false`，或单独关闭某项功能：

```json
{
  "enabled": false,
  "prompt_check_enabled": false,
  "knowledge_capture_enabled": false
}
```

### Q: 确认沉淀时写入哪个知识库？

遵循你的双知识库路由规则——Claude 会先确认目标库（个人 `kj-llm-wiki` 或公司 `loanfe-llm-wiki`），再执行写入。
