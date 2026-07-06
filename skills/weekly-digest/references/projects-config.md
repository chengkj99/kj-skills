# 多项目配置文件说明

## 文件位置

`~/.claude/weekly-digest-projects.json`

## 完整 Schema

```json
{
  "projects": [
    {
      "name": "项目显示名称（必填）",
      "path": "项目绝对路径（必填，必须是 git 仓库）",
      "tags": ["标签1", "标签2"],
      "branch": "指定分支（可选，默认当前分支）",
      "ignore_paths": ["vendor/", "node_modules/"]
    }
  ],
  "defaults": {
    "include_last_week": true,
    "max_commits_per_project": 50,
    "merge_commits": false,
    "all_branches": false
  }
}
```

## 字段说明

### projects[].name
- 类型：string（必填）
- 在周报中显示的项目名称
- 建议简短，2-6 个字

### projects[].path
- 类型：string（必填）
- 项目的绝对路径
- 必须是有效的 git 仓库

### projects[].tags
- 类型：string[]（可选）
- 用于在多项目周报中按标签分组
- 例如：["business", "infra", "tooling"]

### projects[].branch
- 类型：string（可选）
- 指定统计哪个分支
- 不填则使用仓库当前分支

### projects[].ignore_paths
- 类型：string[]（可选）
- 在代码统计中排除的路径前缀
- 常见值：["vendor/", "node_modules/", "dist/"]

### defaults
- 类型：object（可选）
- 所有项目的默认配置，可被项目级配置覆盖

### defaults.include_last_week
- 类型：boolean（默认 true）
- 是否包含上周对比

### defaults.max_commits_per_project
- 类型：number（默认 50）
- 单项目最多采集的提交数

### defaults.merge_commits
- 类型：boolean（默认 false）
- 是否包含 merge commit

### defaults.all_branches
- 类型：boolean（默认 false）
- 是否统计所有分支

## 示例

```json
{
  "projects": [
    {
      "name": "信贷前端 Wiki",
      "path": "/Users/didi/ai_space/loanfe-llm-wiki",
      "tags": ["knowledge", "infra"]
    },
    {
      "name": "信贷 H5",
      "path": "/Users/didi/ai_space/loanfe-h5",
      "tags": ["business", "h5"]
    },
    {
      "name": "营销可视化",
      "path": "/Users/didi/ai_space/loanfe-marketing",
      "tags": ["business", "marketing"],
      "branch": "main"
    }
  ],
  "defaults": {
    "include_last_week": true,
    "max_commits_per_project": 30
  }
}
```
