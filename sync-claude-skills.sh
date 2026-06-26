#!/usr/bin/env bash
# 同步 kj-skills/skills/ 到 ~/.claude/skills/
# 新增 skill 后运行一次，自动补齐缺失的 symlink
# 用法：
#   ./sync-claude-skills.sh              # 同步全部
#   ./sync-claude-skills.sh skill-name   # 只同步单个 skill

SKILLS_SRC="$(cd "$(dirname "$0")/skills" && pwd)"
SKILLS_DST="$HOME/.claude/skills"

added=0
skipped=0
missing=0
failed=0

mkdir -p "$SKILLS_DST"

link_skill() {
  local skill_path="$1"
  local skill_name
  local dst

  skill_name="$(basename "$skill_path")"
  dst="$SKILLS_DST/$skill_name"

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    skipped=$((skipped + 1))
  else
    if ln -s "$skill_path" "$dst"; then
      echo "  linked: $skill_name"
      added=$((added + 1))
    else
      echo "  failed: $skill_name"
      failed=$((failed + 1))
    fi
  fi
}

sync_one() {
  local skill_name="$1"
  local skill_path=""

  if [ -d "$SKILLS_SRC/$skill_name" ]; then
    skill_path="$SKILLS_SRC/$skill_name"
  elif [ -e "$SKILLS_SRC/$skill_name" ]; then
    skill_path="$SKILLS_SRC/$skill_name"
  elif [ -e "$SKILLS_SRC/$skill_name.skill" ]; then
    skill_path="$SKILLS_SRC/$skill_name.skill"
  else
    echo "  missing: $skill_name"
    missing=$((missing + 1))
    return
  fi

  link_skill "$skill_path"
}

if [ "$#" -gt 0 ]; then
  for skill_name in "$@"; do
    sync_one "$skill_name"
  done
else
  for skill_path in "$SKILLS_SRC"/*/; do
    link_skill "$skill_path"
  done

  # 处理 .skill 文件（非目录）
  for skill_path in "$SKILLS_SRC"/*.skill; do
    [ -e "$skill_path" ] || continue
    link_skill "$skill_path"
  done
fi

echo "Done: $added linked, $skipped already exist, $missing missing, $failed failed"
