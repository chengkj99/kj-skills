# ck-skills

Claude / Cursor **Agent Skills** 集合：个人 Wiki 沉淀、AI 日报、内容创作、AI 编程周报。目录结构参考 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)。

## 包含的 Skills

| 目录 | 说明 |
|------|------|
| [skills/wiki-doc-sink](skills/wiki-doc-sink/SKILL.md) | 讨论沉淀到个人 Wiki（需配置 `<WIKI_ROOT>`） |
| [skills/ai-daily-brief](skills/ai-daily-brief/SKILL.md) | 每日 AI 情报日报（脚本 + 评分 rubric） |
| [skills/content-creator](skills/content-creator/SKILL.md) | 长文 / 短视频 / 小红书等工作流 |
| [skills/weekly-report](skills/weekly-report/SKILL.md) | AI 编程周报多格式输出 |
| [skills/markdown-format](skills/markdown-format/SKILL.md) | Pandoc/Word 稿 Markdown 格式化（Obsidian 表格、代码块、标题） |

## Claude Code：Marketplace 安装（推荐）

将下列 `chengkj99/ck-skills` 换成你 fork 后的 `owner/repo`，并同步修改 `.claude-plugin/marketplace.json` 里 `plugins[0].source.repo`（否则 marketplace 仍指向原仓库）：

```text
/plugin marketplace add chengkj99/ck-skills
/plugin install ck-skills@ck-agent-skills
```

若 marketplace 克隆走 SSH 报错，可改用 HTTPS 添加源：

```text
/plugin marketplace add https://github.com/chengkj99/ck-skills.git
/plugin install ck-skills@ck-agent-skills
```

安装后可使用插件命令 **`/ck-help`** 快速查看各 skill 路径。

## Claude Code：本地克隆 + 插件目录

```bash
git clone https://github.com/chengkj99/ck-skills.git
claude --plugin-dir /path/to/ck-skills
```

`--plugin-dir` 指向**仓库根目录**（包含 `.claude-plugin` 的那一层）。

## Cursor 与其它客户端

见 [docs/cursor-setup.md](docs/cursor-setup.md)。

## 单 skill 安装

只需某一目录时，将 `skills/<skill-name>/` **整个文件夹**复制到 Cursor 项目 `.cursor/skills/<skill-name>/` 或全局 skills 目录（见 `docs/cursor-setup.md`）。

## 许可证

MIT，见 [LICENSE](LICENSE)。
