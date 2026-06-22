# 贡献指南

感谢你愿意改进本仓库中的 skills。

## 目录约定

- 每个 skill 位于 `skills/<skill-id>/`，入口为 `SKILL.md`（YAML frontmatter + 正文）。
- 长参考材料放在对应 skill 下的 `references/` 或可执行脚本放在 `scripts/`。
- 修改插件元数据时，请保持 **各端命名一致**：
  - `.claude-plugin/marketplace.json` 顶层 `name`（对应 Claude Code `/plugin install ...@该名`）
  - 同一文件内 `plugins[].name`（对应 `/plugin install 该名@...`）
  - `.claude-plugin/plugin.json` 的 `name`（须与 `plugins[].name` 相同）
  - `.cursor-plugin/plugin.json` 的 `name` 与 `displayName`（Cursor `/add-plugin` 与团队市场）
  - `.cursor-plugin/marketplace.json` 与 Claude 侧 marketplace 的 `plugins[].name` 保持一致
  - `.codex-plugin/plugin.json` 的 `name` 与 `.agents/plugins/marketplace.json` 的 `plugins[].name` 保持一致
  - `.agents/plugins/marketplace.json` 顶层 `name` 对应 Codex `codex plugin add <plugin>@<marketplace>` 的 marketplace 名称

## PR 建议

- 一次 PR 聚焦一个 skill 或一类文档，便于审阅。
- 勿提交真实 API Key、token 或私钥。
- 若改动安装方式或插件 id，请同步更新根目录 `README.md`。
