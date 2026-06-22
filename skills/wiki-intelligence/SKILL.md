---
name: wiki-intelligence
description: >-
  Claude Code hook 系统：在发送提示词前自动评估质量（好提示词存入 wiki，差提示词给出建议），
  回答结束后分析对话价值并引导知识沉淀。适用于任何基于 Markdown 的个人知识库。
disable-model-invocation: false
---

# Wiki Intelligence

一套轻量 Claude Code hook，让每次对话都能为知识库增值。

## 功能

| 时机 | 行为 |
|------|------|
| 发送提示词前（UserPromptSubmit） | 识别高价值意图 → 调用 AI 评分 → 低分给出改进建议；高分静默收藏到 wiki |
| 回答结束后（Stop） | 分析对话价值 → 高分输出要点摘要 → 引导「确认沉淀」 |
| 会话开始（SessionStart） | 清理 24h 过期的会话状态文件 |

## 安装

```bash
# 1. 克隆 kj-skills（或已有则跳过）
git clone https://github.com/your-org/kj-skills.git

# 2. 一键安装
bash kj-skills/skills/wiki-intelligence/install.sh

# 3. 设置 wiki 路径
vim ~/.claude/wiki-intelligence.config.json
# 修改 "wiki_path" 为你的 wiki 绝对路径

# 4. 重启 Claude Code 生效
```

## 配置

唯一配置文件：`~/.claude/wiki-intelligence.config.json`

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `wiki_path` | *(必填)* | wiki 仓库根目录（支持 `~`） |
| `quality_threshold` | `7` | 提示词分数 ≥ 此值则收藏 |
| `knowledge_threshold` | `6` | 对话分数 ≥ 此值则提示沉淀 |
| `high_value_intents` | 见示例 | 触发质量检查的关键词列表 |
| `analysis_model` | `claude-haiku-4-5-20251001` | 用于分析的模型（影响成本） |
| `enabled` | `true` | 全局开关 |
| `prompt_check_enabled` | `true` | 提示词质量检查开关 |
| `knowledge_capture_enabled` | `true` | 知识沉淀捕获开关 |
| `prompt_collection_enabled` | `true` | 好提示词自动收藏开关 |
| `prompt_collection_path` | `wiki/playbooks/prompts` | wiki 内的提示词存储路径（相对） |
| `min_prompt_length` | `20` | 短于此字符数的提示词跳过检查 |

## Wiki 目录约定

好提示词写入 `{wiki_path}/{prompt_collection_path}/` 下按意图分类：

```
wiki/playbooks/prompts/
├── design.md      # 设计/架构类
├── analysis.md    # 分析/研究类
├── planning.md    # 规划/方案类
└── general.md     # 其他
```

知识沉淀（「确认沉淀」触发）由 Claude 侧规则处理写入，hooks 只负责分析与提示。

## 运行测试

```bash
# 跳过需要 claude -p 的集成测试（在 Claude Code 内部运行时使用）
WI_SKIP_CLAUDE_TESTS=1 bash tests/test-wiki-intelligence.sh

# 完整测试（在 Claude Code 外部运行）
bash tests/test-wiki-intelligence.sh
```

## 文件结构

```
hooks/
├── prompt-quality.sh         # UserPromptSubmit hook
├── knowledge-capture.sh      # Stop hook
├── session-start-cleanup.sh  # SessionStart hook
└── lib/
    ├── wiki-intelligence.sh  # 分析引擎（共享库）
    └── wiki-writer.sh        # Wiki 写入工具
tests/
└── test-wiki-intelligence.sh
wiki-intelligence.config.example.json
install.sh
```

## 依赖

- `jq` — JSON 解析（`brew install jq`）
- `python3` — 解析对话记录（macOS 自带）
- `claude` CLI — AI 分析子进程（Claude Code 自带）
