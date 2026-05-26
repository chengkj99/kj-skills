#!/usr/bin/env bash
# git-push skill 示例：检查与暂存流程
# 实际 commit message 须由 Agent 根据 diff 生成后再执行 commit / push

set -euo pipefail

echo "=== 当前状态 ==="
git status
echo ""

echo "=== 最近 5 条提交（对齐风格）==="
git log --oneline -5
echo ""

echo "=== 变更摘要 ==="
git diff --stat
echo ""

echo "=== 暂存全部（按需改为指定文件）==="
# git add -A
# git diff --cached --stat
echo "（示例脚本默认不执行 add/commit/push，避免误操作）"
echo ""

echo "=== 提交示例（由 Agent 替换 message 后执行）==="
cat <<'EOF'
git commit -m "$(cat <<'INNER'
fix(deps): upgrade example-package to 1.2.3

INNER
)"
git push
EOF

echo "=== 流程说明结束 ==="
