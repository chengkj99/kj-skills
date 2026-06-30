#!/usr/bin/env bash
# Unit tests for wiki-intelligence lib

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WI_CONFIG="${TMPDIR:-/tmp}/wiki-intelligence-test-missing-config.json"
rm -f "$WI_CONFIG"
source "${SCRIPT_DIR}/../hooks/lib/wiki-intelligence.sh"

PASS=0
FAIL=0

assert_equals() {
  if [ "$1" = "$2" ]; then
    echo "✅ PASS: $3"
    PASS=$((PASS + 1))
  else
    echo "❌ FAIL: $3"
    echo "   expected: '$2'"
    echo "   got:      '$1'"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_empty() {
  if [ -n "$1" ]; then
    echo "✅ PASS: $2"
    PASS=$((PASS + 1))
  else
    echo "❌ FAIL: $2 (got empty string)"
    FAIL=$((FAIL + 1))
  fi
}

assert_true() {
  if [ "$1" = "0" ]; then
    echo "✅ PASS: $2"
    PASS=$((PASS + 1))
  else
    echo "❌ FAIL: $2 (expected exit 0, got $1)"
    FAIL=$((FAIL + 1))
  fi
}

assert_false() {
  if [ "$1" != "0" ]; then
    echo "✅ PASS: $2"
    PASS=$((PASS + 1))
  else
    echo "❌ FAIL: $2 (expected non-zero exit, got 0)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Wiki Intelligence Tests ==="
echo ""

# Tests will be added per task below

echo "--- Config Loader ---"
wi_load_config
assert_equals "$WI_QUALITY_THRESHOLD" "7" "quality_threshold defaults to 7"
assert_equals "$WI_KNOWLEDGE_THRESHOLD" "6" "knowledge_threshold defaults to 6"
assert_not_empty "$WI_WIKI_PATH" "wiki_path is not empty"
assert_equals "${WI_WIKI_PATH:0:1}" "/" "wiki_path is fully expanded (no leading tilde)"
assert_equals "$WI_ENABLED" "true" "enabled defaults to true"
assert_equals "$WI_STATE_DIR" "${HOME}/.claude/state/wiki-intelligence" "state directory uses wiki-intelligence namespace"

echo ""
echo "--- Intent Detection ---"
wi_is_high_value_intent "帮我设计一个系统架构"; assert_true "$?" "detects '设计' intent"
wi_is_high_value_intent "分析这段代码的性能"; assert_true "$?" "detects '分析' intent"
wi_is_high_value_intent "design a REST API"; assert_true "$?" "detects 'design' intent"
wi_is_high_value_intent "帮我改一下这行代码"; assert_false "$?" "ignores trivial prompt"
wi_is_high_value_intent "ok"; assert_false "$?" "ignores single-word prompt"

if [ "${WI_SKIP_CLAUDE_TESTS:-0}" != "1" ]; then
  echo ""
  echo "--- Claude Call Wrapper (integration, set WI_SKIP_CLAUDE_TESTS=1 to skip) ---"
  result=$(wi_call_claude "Reply with exactly the word: PONG" 15)
  assert_not_empty "$result" "wi_call_claude returns a response"

  echo ""
  echo "--- Prompt Analysis ---"
  result=$(wi_analyze_prompt "帮我做个东西")
  score=$(echo "$result" | jq -r '.score // empty' 2>/dev/null)
  assert_not_empty "$score" "wi_analyze_prompt returns JSON with score field"

  echo ""
  echo "--- Knowledge Analysis ---"
  result=$(wi_analyze_knowledge "User: hi\nAssistant: Hello!")
  score=$(echo "$result" | jq -r '.score // empty' 2>/dev/null)
  assert_not_empty "$score" "wi_analyze_knowledge returns JSON with score field"
else
  echo ""
  echo "--- Claude Call Wrapper / Prompt Analysis / Knowledge Analysis ---"
  echo "⏭  SKIP: WI_SKIP_CLAUDE_TESTS=1 (run outside Claude Code to test AI calls)"
fi

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ]
