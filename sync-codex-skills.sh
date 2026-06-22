#!/usr/bin/env bash
# Sync kj-skills/skills/ into Codex user skills.
# Defaults to $CODEX_HOME/skills, or ~/.codex/skills when CODEX_HOME is unset.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DST="$CODEX_HOME_DIR/skills"

usage() {
  cat <<'EOF'
Usage:
  ./sync-codex-skills.sh              # link all skills
  ./sync-codex-skills.sh <skill> ...  # link selected skills

Environment:
  CODEX_HOME  Override Codex home directory. Defaults to ~/.codex.
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

mkdir -p "$SKILLS_DST"

added=0
skipped=0
missing=0

link_skill() {
  local skill_name="$1"
  local skill_path=""

  if [ -d "$SKILLS_SRC/$skill_name" ]; then
    skill_path="$SKILLS_SRC/$skill_name"
  elif [ -f "$SKILLS_SRC/$skill_name" ]; then
    skill_path="$SKILLS_SRC/$skill_name"
  elif [ -f "$SKILLS_SRC/$skill_name.skill" ]; then
    skill_name="$skill_name.skill"
    skill_path="$SKILLS_SRC/$skill_name"
  else
    echo "  missing: $skill_name" >&2
    missing=$((missing + 1))
    return
  fi

  local dst="$SKILLS_DST/$skill_name"
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    skipped=$((skipped + 1))
  else
    ln -s "$skill_path" "$dst"
    echo "  linked: $skill_name"
    added=$((added + 1))
  fi
}

if [ "$#" -gt 0 ]; then
  for skill_name in "$@"; do
    link_skill "$skill_name"
  done
else
  for skill_path in "$SKILLS_SRC"/*/; do
    [ -d "$skill_path" ] || continue
    link_skill "$(basename "$skill_path")"
  done

  for skill_path in "$SKILLS_SRC"/*.skill; do
    [ -e "$skill_path" ] || continue
    link_skill "$(basename "$skill_path")"
  done
fi

echo "Done: $added linked, $skipped already exist, $missing missing"

if [ "$missing" -gt 0 ]; then
  exit 1
fi
