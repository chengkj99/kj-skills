#!/usr/bin/env bash
# Wiki Intelligence shared analysis library
# Source this file: source ~/.claude/hooks/lib/wiki-intelligence.sh

WI_CONFIG="${WI_CONFIG:-${HOME}/.claude/wiki-intelligence.config.json}"
WI_LOG="${WI_LOG:-${HOME}/.claude/wiki-intelligence.log}"
WI_STATE_DIR="${WI_STATE_DIR:-${HOME}/.claude/state/wiki-intelligence}"

wi_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$WI_LOG" 2>/dev/null || true
}

wi_expand_path() {
  local path="$1"
  echo "${path/#\~/$HOME}"
}

wi_load_config() {
  if [ ! -f "$WI_CONFIG" ]; then
    WI_WIKI_PATH="${HOME}/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki"
    WI_COLLAB_NOTES_PATH="raw/notes/ai-collab"
    WI_QUALITY_THRESHOLD=7
    WI_KNOWLEDGE_THRESHOLD=6
    WI_ANALYSIS_MODEL="claude-haiku-4-5-20251001"
    WI_ENABLED=true
    WI_PROMPT_CHECK_ENABLED=true
    WI_KNOWLEDGE_CAPTURE_ENABLED=true
    WI_PROMPT_COLLECTION_ENABLED=true
    WI_PROMPT_COLLECTION_PATH="wiki/playbooks/prompts"
    WI_MIN_PROMPT_LENGTH=20
    return 0
  fi

  if ! command -v jq &>/dev/null; then
    wi_log "ERROR: jq not found; using defaults"
    WI_WIKI_PATH="${HOME}/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki"
    WI_COLLAB_NOTES_PATH="raw/notes/ai-collab"
    WI_QUALITY_THRESHOLD=7
    WI_KNOWLEDGE_THRESHOLD=6
    WI_ANALYSIS_MODEL="claude-haiku-4-5-20251001"
    WI_ENABLED=true
    WI_PROMPT_CHECK_ENABLED=true
    WI_KNOWLEDGE_CAPTURE_ENABLED=true
    WI_PROMPT_COLLECTION_ENABLED=true
    WI_PROMPT_COLLECTION_PATH="wiki/playbooks/prompts"
    WI_MIN_PROMPT_LENGTH=20
    return 0
  fi

  WI_WIKI_PATH=$(wi_expand_path "$(jq -r '.wiki_path' "$WI_CONFIG")")
  WI_COLLAB_NOTES_PATH=$(jq -r '.collab_notes_path // "raw/notes/ai-collab"' "$WI_CONFIG")
  WI_QUALITY_THRESHOLD=$(jq -r '.quality_threshold // 7' "$WI_CONFIG")
  WI_KNOWLEDGE_THRESHOLD=$(jq -r '.knowledge_threshold // 6' "$WI_CONFIG")
  WI_ANALYSIS_MODEL=$(jq -r '.analysis_model // "claude-haiku-4-5-20251001"' "$WI_CONFIG")
  WI_ENABLED=$(jq -r '.enabled // true' "$WI_CONFIG")
  WI_PROMPT_CHECK_ENABLED=$(jq -r '.prompt_check_enabled // true' "$WI_CONFIG")
  WI_KNOWLEDGE_CAPTURE_ENABLED=$(jq -r '.knowledge_capture_enabled // true' "$WI_CONFIG")
  WI_PROMPT_COLLECTION_ENABLED=$(jq -r '.prompt_collection_enabled // true' "$WI_CONFIG")
  WI_PROMPT_COLLECTION_PATH=$(jq -r '.prompt_collection_path // "wiki/playbooks/prompts"' "$WI_CONFIG")
  WI_MIN_PROMPT_LENGTH=$(jq -r '.min_prompt_length // 20' "$WI_CONFIG")
}

wi_cleanup_stale_state() {
  local state_dir="${WI_STATE_DIR:-${HOME}/.claude/state/wiki-intelligence}"
  [ -d "$state_dir" ] || return 0
  # Remove wiki-intelligence session state files older than 24 hours.
  find "$state_dir" -maxdepth 1 -name 'session-*.json' -mtime +1 -delete 2>/dev/null || true
}

wi_is_high_value_intent() {
  local prompt="$1"
  local intents intent_list matched
  if [ -f "$WI_CONFIG" ]; then
    intents=$(jq -r '.high_value_intents | join("|")' "$WI_CONFIG" 2>/dev/null)
    intent_list=$(jq -r '.high_value_intents[]' "$WI_CONFIG" 2>/dev/null)
  fi
  intents="${intents:-设计|分析|规划|架构|方案|design|analyze|plan|architecture|review}"
  intent_list="${intent_list:-设计
分析
规划
架构
方案
design
analyze
plan
architecture
review}"

  if echo "$prompt" | grep -qiE "($intents)"; then
    # Set global WI_MATCHED_INTENT to first keyword that matches
    WI_MATCHED_INTENT=""
    while IFS= read -r kw; do
      if echo "$prompt" | grep -qi "$kw"; then
        WI_MATCHED_INTENT="$kw"
        break
      fi
    done <<< "$intent_list"
    return 0
  fi
  WI_MATCHED_INTENT=""
  return 1
}

wi_call_claude() {
  local prompt="$1"
  local timeout_sec="${2:-10}"
  local model="${WI_ANALYSIS_MODEL:-claude-haiku-4-5-20251001}"
  local result pid tmpfile elapsed

  tmpfile=$(mktemp)
  claude -p "$prompt" --model "$model" > "$tmpfile" 2>/dev/null &
  pid=$!

  elapsed=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 1
    elapsed=$((elapsed + 1))
    if [ "$elapsed" -ge "$timeout_sec" ]; then
      kill "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      rm -f "$tmpfile"
      wi_log "wi_call_claude: timeout after ${timeout_sec}s (model=$model)"
      echo ""
      return 1
    fi
  done

  result=$(cat "$tmpfile")
  rm -f "$tmpfile"

  if [ -z "$result" ]; then
    wi_log "wi_call_claude: empty response (model=$model)"
    echo ""
    return 1
  fi
  # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
  result=$(echo "$result" | sed '/^```[a-zA-Z]*$/d')
  echo "$result"
}

wi_analyze_prompt() {
  local user_prompt="$1"
  wi_call_claude "你是一个提示词质量评审员。对以下提示词打分（0-10）并给出改进建议。

评分维度：
- 目标清晰度（0-3）：任务目标是否明确？
- 上下文充分度（0-3）：是否提供了足够背景？
- 输出格式说明（0-2）：是否说明了期望的输出形式？
- 约束与边界（0-2）：是否说明了限制条件？

提示词：
<prompt>${user_prompt}</prompt>

只返回 JSON，不要有任何其他文字：{\"score\": <0到10的整数>, \"issues\": [\"<问题1>\", \"<问题2>\"], \"suggestion\": \"<一句话改进建议>\"}" 15
}

wi_analyze_knowledge() {
  local conversation="$1"
  wi_call_claude "你是一个知识管理专家。判断以下对话是否包含值得长期保存的知识。

评分维度：
- 概念深度（0-3）：是否解释了非显而易见的原理或概念？
- 实践价值（0-3）：是否包含可复用的方法、框架或决策标准？
- 新颖性（0-2）：相对于常识，是否提供了新视角？
- 结构性（0-2）：内容是否有清晰结构，便于日后检索？

对话内容：
<conversation>${conversation}</conversation>

只返回 JSON，不要有任何其他文字：{\"score\": <0到10的整数>, \"value_type\": \"<concept|framework|decision|pattern>\", \"bullets\": [\"<要点1>\", \"<要点2>\", \"<要点3>\"]}" 20
}
