# Cursor 中使用本仓库 Skills

本仓库主要面向 **Claude Code 插件**（`.claude-plugin/`）。在 Cursor 中可将单个 skill 当作 **规则/技能包** 使用。

## 项目级（推荐团队协作）

1. 在项目根创建目录：`.cursor/skills/`（若不存在）。
2. 将本仓库中某一 skill **整目录**复制进去，例如：
   - `skills/content-creator/` → `<你的项目>/.cursor/skills/content-creator/`
3. 在对话里 **@** 对应 skill，或按各 `SKILL.md` 中的触发说明使用。

## 全局（个人所有项目）

将 `skills/<name>/` 复制到 Cursor 全局 skills 目录（因 Cursor 版本差异，路径可能为 `~/.cursor/skills-cursor/<name>/` 或官方文档中的最新路径），以你本机 Cursor 设置为准。

## 与 Claude Code 同时使用时

同一 skill 目录可被复制到不同位置；注意维护两份时的同步成本，建议以本 Git 仓库为单一事实来源。
