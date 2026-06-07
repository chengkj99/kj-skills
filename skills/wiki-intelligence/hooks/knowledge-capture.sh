#!/usr/bin/env bash
# Wiki Intelligence: Stop hook
# Analyzes the last conversation turn for valuable knowledge and prompts user to save

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${HOOKS_DIR}/lib/wiki-intelligence.sh"
source "${HOOKS_DIR}/lib/wiki-writer.sh"

# Always exit 0 — never block Claude Code
trap 'exit 0' ERR

# Parse stdin JSON
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null || echo "")
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")

# Load config; bail if disabled
wi_load_config
[ "$WI_ENABLED" = "true" ] || exit 0
[ "$WI_KNOWLEDGE_CAPTURE_ENABLED" = "true" ] || exit 0

# Only process sessions flagged as high-value by prompt-quality.sh
[ -n "$SESSION_ID" ] || exit 0
STATE_FILE="${WI_STATE_DIR}/session-${SESSION_ID}.json"
[ -f "$STATE_FILE" ] || exit 0

# Transcript must exist to extract conversation
[ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ] || exit 0

# Extract last 3 user+assistant exchanges as plain text (max 3000 chars total)
CONVERSATION=$(python3 - "$TRANSCRIPT_PATH" <<'PYEOF'
import sys, json

path = sys.argv[1]
entries = []
try:
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                if d.get('type') in ('user', 'assistant'):
                    entries.append(d)
            except Exception:
                pass
except Exception:
    sys.exit(0)

recent = entries[-6:]
parts = []
for e in recent:
    role = e['type']
    content = e.get('message', {}).get('content', '')
    if isinstance(content, list):
        text = ' '.join(
            c.get('text', '') for c in content
            if isinstance(c, dict) and c.get('type') == 'text'
        )
    else:
        text = str(content) if content else ''
    text = text.strip()[:800]
    if text:
        parts.append(f'[{role}]: {text}')

print('\n'.join(parts))
PYEOF
)

[ -n "$CONVERSATION" ] || exit 0

# Run knowledge value analysis
RAW_RESULT=$(wi_analyze_knowledge "$CONVERSATION")
[ -n "$RAW_RESULT" ] || exit 0

SCORE=$(echo "$RAW_RESULT" | jq -r '.score // 0' 2>/dev/null | grep -o '^[0-9]*' || echo "0")
SCORE="${SCORE:-0}"

# Below threshold — skip silently
[ "$SCORE" -ge "${WI_KNOWLEDGE_THRESHOLD:-6}" ] 2>/dev/null || exit 0

VALUE_TYPE=$(echo "$RAW_RESULT" | jq -r '.value_type // "knowledge"' 2>/dev/null || echo "knowledge")
BULLET1=$(echo "$RAW_RESULT" | jq -r '.bullets[0] // ""' 2>/dev/null || echo "")
BULLET2=$(echo "$RAW_RESULT" | jq -r '.bullets[1] // ""' 2>/dev/null || echo "")
BULLET3=$(echo "$RAW_RESULT" | jq -r '.bullets[2] // ""' 2>/dev/null || echo "")

BULLETS_JSON=$(echo "$RAW_RESULT" | jq -c '.bullets // []' 2>/dev/null || echo "[]")

# Write bullets to session state for Claude to use when user says "确认沉淀"
ww_write_session_bullets "$STATE_FILE" "$BULLETS_JSON" "$VALUE_TYPE" "$SCORE"

# Output soft advisory to stderr
{
  echo "📖 本轮对话有沉淀价值（${SCORE}/10，类型：${VALUE_TYPE}）"
  echo "   要点："
  [ -n "$BULLET1" ] && echo "   • ${BULLET1}"
  [ -n "$BULLET2" ] && echo "   • ${BULLET2}"
  [ -n "$BULLET3" ] && echo "   • ${BULLET3}"
  echo "   回复「确认沉淀」将保存到 wiki，或忽略此条"
} >&2

exit 0
