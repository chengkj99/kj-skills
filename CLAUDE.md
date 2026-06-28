# kj-skills 项目规范

## 语言规范

本仓库所有 `AGENTS.md` 文件（包括子目录下的）**必须使用中文**撰写。新增 skill 或子模块时，若需创建 `AGENTS.md`，同样使用中文。技术术语、命令、代码标识符保持原文，说明文字用中文。

## local-stt-transcription 维护规则

- 统一版本位于 `skills/local-stt-transcription/`；项目仓库中的 `.agents/skills/local-stt-transcription` 应通过 symlink 指向这里，避免两处分叉。
- 该 skill 输出已发布短视频的最终校对文字稿，默认用于 `raw/studio/transcripts/`；原始 STT 草稿只作为临时中间产物，不作为最终产物保存。
- `raw/studio/transcripts/` 是已发布内容资产库，可用于连载选题规划；从中提炼选题时要标注来源文字稿、所属系列和下一集角度。
- 每次发现新的 STT 常见错词，要更新 `skills/local-stt-transcription/references/transcript-polish.md`，让后续转写持续受益。
- 外部 `jianchang512/stt` runtime 不要 vendor 进本仓库；新机初始化使用 `scripts/bootstrap_stt_runtime.sh`。
