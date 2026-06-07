#!/usr/bin/env bash
# Wiki Intelligence: UserPromptSubmit hook
# Checks prompt quality and auto-saves good prompts to wiki

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${HOOKS_DIR}/lib/wiki-intelligence.sh"
source "${HOOKS_DIR}/lib/wiki-writer.sh"

# Always exit 0 — never block Claude Code
trap 'exit 0' ERR

# Parse stdin JSON
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""' 2>/dev/null || echo "")
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")

# Load config; bail if disabled
wi_load_config
[ "$WI_ENABLED" = "true" ] || exit 0
[ "$WI_PROMPT_CHECK_ENABLED" = "true" ] || exit 0

# Skip short prompts
PROMPT_LEN="${#PROMPT}"
[ "$PROMPT_LEN" -ge "${WI_MIN_PROMPT_LENGTH:-20}" ] || exit 0

# Skip if not a high-value intent
wi_is_high_value_intent "$PROMPT" || exit 0

# Run quality analysis
RAW_RESULT=$(wi_analyze_prompt "$PROMPT")
[ -n "$RAW_RESULT" ] || exit 0

SCORE=$(echo "$RAW_RESULT" | jq -r '.score // 0' 2>/dev/null | grep -o '^[0-9]*' || echo "0")
SCORE="${SCORE:-0}"
ISSUES=$(echo "$RAW_RESULT" | jq -r '.issues[0] // ""' 2>/dev/null || echo "")
SUGGESTION=$(echo "$RAW_RESULT" | jq -r '.suggestion // ""' 2>/dev/null || echo "")

# Write session state atomically (for knowledge-capture hook to read later)
STATE_FILE="${WI_STATE_DIR}/session-${SESSION_ID}.json"
mkdir -p "$WI_STATE_DIR"
TMP=$(mktemp "${STATE_FILE}.XXXXXX")
printf '{"session_id":"%s","prompt":%s,"quality_score":%s,"timestamp":"%s"}\n' \
  "$SESSION_ID" \
  "$(echo "$PROMPT" | jq -Rs .)" \
  "$SCORE" \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$TMP" && mv "$TMP" "$STATE_FILE" || rm -f "$TMP"

# Use intent already matched by wi_is_high_value_intent (set as WI_MATCHED_INTENT global)
INTENT="${WI_MATCHED_INTENT:-}"

# If score is high enough → save to prompt collection silently
if [ "$WI_PROMPT_COLLECTION_ENABLED" = "true" ] && [ "${SCORE:-0}" -ge "${WI_QUALITY_THRESHOLD:-7}" ] 2>/dev/null; then
  ww_save_good_prompt "$WI_WIKI_PATH" "$WI_PROMPT_COLLECTION_PATH" "$PROMPT" "$INTENT" "$SCORE"
  exit 0
fi

# If score is below threshold → show soft advisory
if [ "${SCORE:-0}" -lt "${WI_QUALITY_THRESHOLD:-7}" ] 2>/dev/null && [ -n "$ISSUES" ]; then
  echo "💡 提示词建议（${SCORE}/10）：${ISSUES}${SUGGESTION:+ — $SUGGESTION}"
fi

exit 0
