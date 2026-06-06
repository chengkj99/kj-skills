#!/usr/bin/env bash
# 同步 kj-skills/skills/ 到 ~/.claude/skills/
# 新增 skill 后运行一次，自动补齐缺失的 symlink

SKILLS_SRC="$(cd "$(dirname "$0")/skills" && pwd)"
SKILLS_DST="$HOME/.claude/skills"

added=0
skipped=0

for skill_path in "$SKILLS_SRC"/*/; do
  skill_name="$(basename "$skill_path")"
  dst="$SKILLS_DST/$skill_name"

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    skipped=$((skipped + 1))
  else
    ln -s "$skill_path" "$dst"
    echo "  linked: $skill_name"
    added=$((added + 1))
  fi
done

# 处理 .skill 文件（非目录）
for skill_path in "$SKILLS_SRC"/*.skill; do
  [ -e "$skill_path" ] || continue
  skill_name="$(basename "$skill_path")"
  dst="$SKILLS_DST/$skill_name"

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    skipped=$((skipped + 1))
  else
    ln -s "$skill_path" "$dst"
    echo "  linked: $skill_name"
    added=$((added + 1))
  fi
done

echo "Done: $added linked, $skipped already exist"
