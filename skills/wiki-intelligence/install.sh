#!/usr/bin/env bash
# Wiki Intelligence — installer
# Copies hooks to ~/.claude/hooks/ and registers them in ~/.claude/settings.json

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOOKS="${HOME}/.claude/hooks"
CLAUDE_CONFIG="${HOME}/.claude/wiki-intelligence.config.json"
SETTINGS="${HOME}/.claude/settings.json"

# ── Preflight ─────────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq" >&2
  exit 1
fi

echo "=== Wiki Intelligence Installer ==="

# ── Copy hooks ────────────────────────────────────────────────────────
echo "Copying hooks to ${CLAUDE_HOOKS}..."
mkdir -p "${CLAUDE_HOOKS}/lib"
cp "${SKILL_DIR}/hooks/prompt-quality.sh"        "${CLAUDE_HOOKS}/prompt-quality.sh"
cp "${SKILL_DIR}/hooks/knowledge-capture.sh"     "${CLAUDE_HOOKS}/knowledge-capture.sh"
cp "${SKILL_DIR}/hooks/session-start-cleanup.sh" "${CLAUDE_HOOKS}/session-start-cleanup.sh"
cp "${SKILL_DIR}/hooks/lib/wiki-intelligence.sh" "${CLAUDE_HOOKS}/lib/wiki-intelligence.sh"
cp "${SKILL_DIR}/hooks/lib/wiki-writer.sh"       "${CLAUDE_HOOKS}/lib/wiki-writer.sh"
chmod +x "${CLAUDE_HOOKS}/prompt-quality.sh" \
         "${CLAUDE_HOOKS}/knowledge-capture.sh" \
         "${CLAUDE_HOOKS}/session-start-cleanup.sh" \
         "${CLAUDE_HOOKS}/lib/wiki-intelligence.sh" \
         "${CLAUDE_HOOKS}/lib/wiki-writer.sh"
echo "✅ Hooks copied"

# ── Config file ───────────────────────────────────────────────────────
if [ ! -f "$CLAUDE_CONFIG" ]; then
  cp "${SKILL_DIR}/wiki-intelligence.config.example.json" "$CLAUDE_CONFIG"
  echo "✅ Config created at ${CLAUDE_CONFIG}"
  echo "   Edit wiki_path to point to your wiki before restarting Claude Code."
else
  echo "⏭  Config already exists at ${CLAUDE_CONFIG} — not overwritten"
fi

# ── Register hooks in settings.json ───────────────────────────────────
if [ ! -f "$SETTINGS" ]; then
  echo '{"hooks":{}}' > "$SETTINGS"
fi

# Helper: add a hook entry if not already present
add_hook() {
  local event="$1"
  local command="$2"
  local already
  already=$(jq --arg cmd "$command" \
    ".hooks.${event}? // [] | map(.hooks[]?.command) | map(select(. == \$cmd)) | length" \
    "$SETTINGS" 2>/dev/null || echo "0")
  if [ "$already" = "0" ]; then
    local tmp
    tmp=$(mktemp "${SETTINGS}.XXXXXX")
    jq --arg event "$event" --arg cmd "$command" \
      '.hooks[$event] = ([{"matcher":"","hooks":[{"type":"command","command":$cmd}]}] + (.hooks[$event] // []))' \
      "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    echo "✅ Registered ${command} → ${event}"
  else
    echo "⏭  ${command} already registered in ${event}"
  fi
}

add_hook "SessionStart"      "~/.claude/hooks/session-start-cleanup.sh"
add_hook "UserPromptSubmit"  "~/.claude/hooks/prompt-quality.sh"
add_hook "Stop"              "~/.claude/hooks/knowledge-capture.sh"

echo ""
echo "=== Installation complete ==="
echo "Restart Claude Code to activate Wiki Intelligence."
echo ""
echo "Next step: set your wiki path in ${CLAUDE_CONFIG}"
echo "  \"wiki_path\": \"~/path/to/your/wiki\""
