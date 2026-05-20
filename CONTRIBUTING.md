# 贡献指南

感谢你愿意改进本仓库中的 skills。

## 目录约定

- 每个 skill 位于 `skills/<skill-id>/`，入口为 `SKILL.md`（YAML frontmatter + 正文）。
- 长参考材料放在对应 skill 下的 `references/` 或可执行脚本放在 `scripts/`。
- 修改 Claude Code 插件元数据时，请保持 **三处命名一致**：
  - `.claude-plugin/marketplace.json` 顶层 `name`（对应 `/plugin install ...@该名`）
  - 同一文件内 `plugins[].name`（对应 `/plugin install 该名@...`）
  - `.claude-plugin/plugin.json` 的 `name`（须与 `plugins[].name` 相同）

## PR 建议

- 一次 PR 聚焦一个 skill 或一类文档，便于审阅。
- 勿提交真实 API Key、token 或私钥。
- 若改动安装方式或插件 id，请同步更新根目录 `README.md`。
