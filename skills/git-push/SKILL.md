---
name: git-push
description: >-
  一键完成 git 暂存、生成 Conventional Commits 风格提交说明、提交并推送到远程。
  在用户说「push 代码」「提交代码」「commit 并 push」「自动提交」「git add commit push」
  或明确要求把当前改动推到远程时使用。
---

# Git Push（提交并推送）

自动化完整 git 工作流：检查状态 → 分析 diff → 生成提交说明 → `git add` → `git commit` → `git push`。

## 适用场景

- 用户**明确要求**提交、推送或「一条龙」完成 add/commit/push
- 需要基于当前 diff 自动生成符合仓库风格的 commit message

若用户仅问「改了什么」「要不要提交」，**不要**执行本 skill，只回答或展示 `git status` / `git diff`。

## 硬性约束（必须遵守）

1. **仅在用户明确要求时**才 `git add` / `git commit` / `git push`；未明确要求则停在分析或建议阶段。
2. **禁止**修改 git 配置（`git config` 等）。
3. **禁止**对 `main` / `master` 执行 `push --force`；若用户要求强推，先警告风险。
4. **禁止**默认使用 `--no-verify` / `--no-gpg-sign`，除非用户明确要求跳过 hook。
5. **禁止**提交明显含密钥的文件（`.env`、`*credentials*`、`*.pem` 等）；发现后警告并排除，除非用户确认仍要提交。
6. 用户规则要求「不要 amend」时：仅在用户明确要求 amend、且 HEAD 为本会话创建且未推送时方可 `--amend`；hook 失败或 commit 被拒后**新建 commit**，不要 amend。
7. **不要**在用户未要求时 `git push` 到远程。

## 工作流

### 1. 检查状态

并行或依次执行：

```bash
git status
git diff --stat
git log --oneline -5
```

确认：是否有可提交改动、当前分支、与远程跟踪关系、近期 commit 风格。

### 2. 分析变更

```bash
git diff
git diff --cached
```

对新文件结合 `git diff --stat` 与 Read 理解意图。提交说明类型与示例见 [`references/commit-patterns.md`](references/commit-patterns.md)。

### 3. 生成提交说明

采用 [Conventional Commits](https://www.conventionalcommits.org/)：

```text
<type>(<scope>): <简短描述>

[可选正文]

[可选 Co-Authored-By 行]
```

**type**：`feat` | `fix` | `docs` | `style` | `refactor` | `test` | `chore`

**规则**：

- 根据 diff 判断 type 与 scope（模块/目录名）
- 标题约 50–72 字符，说明「做了什么、为何」，与 `git log` 近期风格一致
- 正文可选；破坏性变更用 `!` 或 `BREAKING CHANGE:` 注明
- `Co-Authored-By` 仅在与用户约定或项目惯例需要时添加，勿硬编码错误模型名

### 4. 暂存与提交

只暂存与本次任务相关的文件；用户说「全部提交」时用：

```bash
git add -A
```

提交（HEREDOC 保证多行格式）：

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

EOF
)"
```

- 若无改动可提交：告知用户，**不要**空提交
- pre-commit hook 失败：修复问题后**新建 commit**，不要 amend（除非满足用户 amend 规则）

### 5. 推送到远程

```bash
git push
```

或指定上游：

```bash
git push -u origin "$(git branch --show-current)"
```

**推送前检查**：

- 若本地落后远程：提示先 `git pull --rebase`（或用户偏好的合并方式），**不要**自动 force push
- 冲突或 push 被拒：说明原因，给出修复步骤，不擅自 force

## 错误处理

| 情况 | 处理 |
|------|------|
| 无改动 | 说明工作区干净，结束 |
| commit 失败 | 读 hook/错误信息，修代码或格式后重新 commit |
| push 失败 | 检查权限、分支保护、是否需 pull/rebase |
| 含敏感文件 | 列出路径，建议加入 `.gitignore`，默认不提交 |

## 示例

**用户**：「push 代码」

1. `git status` → 2 个修改文件  
2. diff → 依赖安全升级  
3. 生成：`fix(deps): upgrade handlebars to 4.7.9 for security fix`  
4. `git add` → `git commit` → `git push`

## 参考

- [`references/commit-patterns.md`](references/commit-patterns.md) — 按变更类型匹配 commit 模板  
- [`examples/workflow.sh`](examples/workflow.sh) — 可本地运行的检查与暂存示例（提交/推送需 Agent 按 diff 生成 message 后执行）
