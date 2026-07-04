#!/usr/bin/env bash
# Wiki writer utility library

WI_LOG="${WI_LOG:-${HOME}/.claude/wiki-intelligence.log}"

ww_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [writer] $*" >> "$WI_LOG" 2>/dev/null || true
}

ww_resolve_path() {
  local path="$1"
  echo "${path/#\~/$HOME}"
}

ww_intent_to_file() {
  local intent="$1"
  case "$intent" in
    *设计*|*design*|*架构*|*architecture*) echo "design.md" ;;
    *分析*|*analysis*|*analyze*) echo "analysis.md" ;;
    *规划*|*plan*|*planning*|*方案*) echo "planning.md" ;;
    *) echo "general.md" ;;
  esac
}

ww_is_prompt_collection_safe() {
  local prompt_text="$1"
  local filepath="$2"
  local prompt_len="${#prompt_text}"
  local max_chars="${WI_PROMPT_COLLECTION_MAX_ENTRY_CHARS:-4000}"
  local max_lines="${WI_PROMPT_COLLECTION_MAX_ENTRY_LINES:-120}"
  local max_file_bytes="${WI_PROMPT_COLLECTION_MAX_FILE_BYTES:-102400}"
  local max_repeat_count="${WI_PROMPT_COLLECTION_MAX_REPEAT_COUNT:-10}"
  local line_count repeat_count current_bytes estimated_bytes

  if [ "$prompt_len" -gt "$max_chars" ]; then
    ww_log "Skipping prompt collection: entry too large (${prompt_len} > ${max_chars} chars)"
    return 1
  fi

  line_count=$(printf '%s\n' "$prompt_text" | wc -l | tr -d ' ')
  if [ "${line_count:-0}" -gt "$max_lines" ]; then
    ww_log "Skipping prompt collection: too many lines (${line_count} > ${max_lines})"
    return 1
  fi

  if printf '%s\n' "$prompt_text" | grep -qiE '你是一个提示词质量评审员|只返回 JSON|<prompt>|</prompt>|"score"[[:space:]]*:|score/issues/suggestion'; then
    ww_log "Skipping prompt collection: looks like prompt-review evaluator text"
    return 1
  fi

  repeat_count=$(printf '%s\n' "$prompt_text" | awk 'length($0) >= 20 { c[$0]++ } END { max=0; for (line in c) if (c[line] > max) max=c[line]; print max+0 }')
  if [ "${repeat_count:-0}" -gt "$max_repeat_count" ]; then
    ww_log "Skipping prompt collection: repeated line count too high (${repeat_count} > ${max_repeat_count})"
    return 1
  fi

  current_bytes=0
  if [ -f "$filepath" ]; then
    current_bytes=$(wc -c < "$filepath" | tr -d ' ')
  fi
  estimated_bytes=$(( ${current_bytes:-0} + prompt_len + 128 ))
  if [ "$estimated_bytes" -gt "$max_file_bytes" ]; then
    ww_log "Skipping prompt collection: target file would exceed ${max_file_bytes} bytes (${estimated_bytes})"
    return 1
  fi

  return 0
}

ww_save_good_prompt() {
  local wiki_path="$1"
  local collection_rel_path="$2"
  local prompt_text="$3"
  local intent="$4"
  local score="$5"

  local prompt_len="${#prompt_text}"
  local min_len="${WI_MIN_PROMPT_LENGTH:-20}"
  if [ "$prompt_len" -lt "$min_len" ]; then
    ww_log "Skipping short prompt (${prompt_len} < ${min_len} chars)"
    return 0
  fi

  local full_dir="${wiki_path}/${collection_rel_path}"
  mkdir -p "$full_dir" 2>/dev/null || { ww_log "Failed to create dir: $full_dir"; return 1; }

  local target_file
  target_file=$(ww_intent_to_file "$intent")
  local filepath="${full_dir}/${target_file}"
  local entry_date
  entry_date=$(date '+%Y-%m-%d')
  local entry_intent="${intent:-未分类}"

  if ! ww_is_prompt_collection_safe "$prompt_text" "$filepath"; then
    return 0
  fi

  if [ ! -f "$filepath" ]; then
    echo "# ${target_file%.md} 类好提示词" > "$filepath"
    echo "" >> "$filepath"
    echo "> 由 Wiki Intelligence 自动收录，评分 ≥ 7/10" >> "$filepath"
    echo "" >> "$filepath"
  fi

  printf '\n### %s — %s\n> %s\n\n**质量评分**：%s/10\n' \
    "$entry_date" "$entry_intent" "$prompt_text" "$score" >> "$filepath"

  ww_log "Saved good prompt to ${target_file} (score=${score}, intent=${intent})"
}

ww_write_session_bullets() {
  local state_file="$1"
  local bullets_json="$2"
  local value_type="$3"
  local score="$4"

  [ -f "$state_file" ] || return 0

  local tmp
  tmp=$(mktemp "${state_file}.XXXXXX")
  if ! jq --argjson bullets "$bullets_json" \
       --arg value_type "$value_type" \
       --arg score "$score" \
       '. + {"knowledge_bullets": $bullets, "knowledge_value_type": $value_type, "knowledge_score": ($score | tonumber)}' \
       "$state_file" > "$tmp" 2>/dev/null; then
    ww_log "ww_write_session_bullets: jq failed (score=${score}, state=${state_file})"
    rm -f "$tmp"
    return 1
  fi
  mv "$tmp" "$state_file"
}
