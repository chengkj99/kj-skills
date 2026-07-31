#!/usr/bin/env bash
# scan-repos.sh — 扫描目录中当前周有非 merge 提交的 Git 仓库
# 用法：./scan-repos.sh <扫描目录> [本周起始日 YYYY-MM-DD]

set -euo pipefail

SCAN_ROOT="${1:-}"
WEEK_START="${2:-}"

if [[ -z "$SCAN_ROOT" ]]; then
  echo "用法：$0 <扫描目录> [本周起始日 YYYY-MM-DD]" >&2
  exit 2
fi

if [[ ! -d "$SCAN_ROOT" ]]; then
  echo "扫描目录不存在或不是目录：$SCAN_ROOT" >&2
  exit 2
fi

if [[ -z "$WEEK_START" ]]; then
  if date -v-monday +%Y-%m-%d >/dev/null 2>&1; then
    WEEK_START=$(date -v-monday +%Y-%m-%d)
  else
    WEEK_START=$(date -d "last monday" +%Y-%m-%d)
    if [[ "$(date +%u)" -eq 1 ]]; then
      WEEK_START=$(date +%Y-%m-%d)
    fi
  fi
fi

if date -v+1d +%Y-%m-%d >/dev/null 2>&1; then
  WEEK_END=$(date -v+1d +%Y-%m-%d)
else
  WEEK_END=$(date -d "tomorrow" +%Y-%m-%d)
fi

printf 'project\tpath\tcommits\tlatest_subject\n'

while IFS= read -r -d '' git_dir; do
  repo_path=$(dirname "$git_dir")
  if ! git -C "$repo_path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    continue
  fi

  commit_count=$(git -C "$repo_path" rev-list --count --no-merges \
    --since="$WEEK_START" --until="$WEEK_END" HEAD 2>/dev/null || printf '0')
  if [[ "$commit_count" -eq 0 ]]; then
    continue
  fi

  latest_subject=$(git -C "$repo_path" log -1 --no-merges --format='%s' \
    --since="$WEEK_START" --until="$WEEK_END" 2>/dev/null || true)
  printf '%s\t%s\t%s\t%s\n' "$(basename "$repo_path")" "$repo_path" "$commit_count" "$latest_subject"
done < <(find "$SCAN_ROOT" -type d -name .git -prune -print0) | \
  LC_ALL=C sort -t $'\t' -k3,3nr -k1,1
