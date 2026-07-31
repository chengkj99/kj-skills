#!/usr/bin/env bash
# collect.sh — 跨平台 git 数据采集脚本
# 用于 weekly-digest Skill 的 Step 1
#
# 用法：
#   ./collect.sh [项目路径] [本周起始日 YYYY-MM-DD] [上周起始日 YYYY-MM-DD]
#
# 示例：
#   ./collect.sh /path/to/repo 2026-06-02 2026-05-26
#   ./collect.sh  # 使用当前目录和自动计算日期

set -euo pipefail

REPO_PATH="${1:-.}"
THIS_WEEK_START="${2:-}"
LAST_WEEK_START="${3:-}"

cd "$REPO_PATH"

# ─── 日期计算（兼容 macOS 和 Linux） ───

if [[ -z "$THIS_WEEK_START" ]]; then
  if date -v-monday +%Y-%m-%d &>/dev/null; then
    # macOS
    THIS_WEEK_START=$(date -v-monday +%Y-%m-%d)
  else
    # Linux
    THIS_WEEK_START=$(date -d "last monday" +%Y-%m-%d)
  fi
  # 如果今天是周一，last monday 会回到上周一，需要修正
  TODAY_DOW=$(date +%u)
  if [[ "$TODAY_DOW" -eq 1 ]]; then
    THIS_WEEK_START=$(date +%Y-%m-%d)
  fi
fi

if [[ -z "$LAST_WEEK_START" ]]; then
  if date -v-7d +%Y-%m-%d &>/dev/null; then
    LAST_WEEK_START=$(date -v-7d -j -f "%Y-%m-%d" "$THIS_WEEK_START" +%Y-%m-%d 2>/dev/null || \
      python3 -c "from datetime import datetime, timedelta; d=datetime.strptime('$THIS_WEEK_START','%Y-%m-%d'); print((d-timedelta(days=7)).strftime('%Y-%m-%d'))")
  else
    LAST_WEEK_START=$(date -d "$THIS_WEEK_START -7 days" +%Y-%m-%d)
  fi
fi

# 计算本周结束日期（明天）
if date -v+1d +%Y-%m-%d &>/dev/null; then
  THIS_WEEK_END=$(date -v+1d +%Y-%m-%d)
else
  THIS_WEEK_END=$(date -d "tomorrow" +%Y-%m-%d)
fi

# ─── 采集函数 ───

collect_commits() {
  local since="$1" until="$2"
  git log --oneline --since="$since" --until="$until" \
    --format="%h|%ad|%an|%s" --date=short --no-merges 2>/dev/null || true
}

collect_stats() {
  local since="$1" until="$2"
  git log --since="$since" --until="$until" \
    --shortstat --format="" --no-merges 2>/dev/null \
    | awk '/files? changed/ {f+=$1; i+=$4; d+=$6} END {print f,i,d}'
}

# 输出：姓名|邮箱|提交数|新增行|删除行（每位 author 独立汇总）
collect_contributors() {
  local since="$1" until="$2"
  git log --since="$since" --until="$until" --no-merges \
    --format='__AUTHOR__%an|%ae' --shortstat 2>/dev/null \
    | awk '
      /^__AUTHOR__/ {
        split(substr($0, 11), author, "|")
        key = author[1] SUBSEP author[2]
        names[key] = author[1]
        emails[key] = author[2]
        commits[key]++
        current = key
        next
      }
      /files? changed/ && current != "" {
        if ($4 ~ /^[0-9]+$/) insertions[current] += $4
        if ($6 ~ /^[0-9]+$/) deletions[current] += $6
      }
      END {
        for (key in commits) {
          printf "%s|%s|%d|%d|%d\\n", names[key], emails[key], commits[key], insertions[key], deletions[key]
        }
      }
    ' | sort -t'|' -k3,3nr -k1,1
}

# 将多行文本编码为 JSON 字符串内容（换行转义为字面量 \\n）。
json_escape() {
  sed -e 's/\\\\/\\\\\\\\/g' -e 's/"/\\\\"/g' \
    | awk 'BEGIN { first = 1 } { if (!first) printf "\\\\n"; printf "%s", $0; first = 0 }'
}

# ─── 输出 JSON ───

# 项目名
PROJECT_NAME=$(basename "$(pwd)")

# 本周
THIS_WEEK_COMMITS=$(collect_commits "$THIS_WEEK_START" "$THIS_WEEK_END")
THIS_WEEK_STATS=$(collect_stats "$THIS_WEEK_START" "$THIS_WEEK_END")
THIS_WEEK_FILES=$(echo "$THIS_WEEK_STATS" | awk '{print $1}')
THIS_WEEK_INSERTS=$(echo "$THIS_WEEK_STATS" | awk '{print $2}')
THIS_WEEK_DELETES=$(echo "$THIS_WEEK_STATS" | awk '{print $3}')
THIS_WEEK_COUNT=$(echo "$THIS_WEEK_COMMITS" | grep -c '.' 2>/dev/null || echo 0)
THIS_WEEK_CONTRIBUTORS=$(collect_contributors "$THIS_WEEK_START" "$THIS_WEEK_END")

# 上周
LAST_WEEK_COMMITS=$(collect_commits "$LAST_WEEK_START" "$THIS_WEEK_START")
LAST_WEEK_STATS=$(collect_stats "$LAST_WEEK_START" "$THIS_WEEK_START")
LAST_WEEK_FILES=$(echo "$LAST_WEEK_STATS" | awk '{print $1}')
LAST_WEEK_INSERTS=$(echo "$LAST_WEEK_STATS" | awk '{print $2}')
LAST_WEEK_DELETES=$(echo "$LAST_WEEK_STATS" | awk '{print $3}')
LAST_WEEK_COUNT=$(echo "$LAST_WEEK_COMMITS" | grep -c '.' 2>/dev/null || echo 0)
LAST_WEEK_CONTRIBUTORS=$(collect_contributors "$LAST_WEEK_START" "$THIS_WEEK_START")

cat <<EOF
{
  "project": "$(printf '%s' "$PROJECT_NAME" | json_escape)",
  "this_week": {
    "start": "$THIS_WEEK_START",
    "end": "$THIS_WEEK_END",
    "commit_count": $THIS_WEEK_COUNT,
    "files_changed": ${THIS_WEEK_FILES:-0},
    "insertions": ${THIS_WEEK_INSERTS:-0},
    "deletions": ${THIS_WEEK_DELETES:-0},
    "commits": "$(printf '%s' "$THIS_WEEK_COMMITS" | json_escape)",
    "contributors": "$(printf '%s' "$THIS_WEEK_CONTRIBUTORS" | json_escape)"
  },
  "last_week": {
    "start": "$LAST_WEEK_START",
    "end": "$THIS_WEEK_START",
    "commit_count": $LAST_WEEK_COUNT,
    "files_changed": ${LAST_WEEK_FILES:-0},
    "insertions": ${LAST_WEEK_INSERTS:-0},
    "deletions": ${LAST_WEEK_DELETES:-0},
    "commits": "$(printf '%s' "$LAST_WEEK_COMMITS" | json_escape)",
    "contributors": "$(printf '%s' "$LAST_WEEK_CONTRIBUTORS" | json_escape)"
  }
}
EOF
