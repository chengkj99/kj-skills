# 部署集成说明

本技能可独立使用（只生成日报），也可与前端网站集成实现自动发布。

---

## 独立使用（无集成）

只做内容生成，输出 Markdown。不执行阶段 4（写入+更新）。

---

## 与 ai-programming-guide 网站集成

### 集成说明

- 网站项目根目录用占位符 `<APP_DIR>` 表示（例：`<你的仓库>/apps/ai-programming-guide`）。使用前设置为你自己的绝对路径。
- 维护者线上地址示例：`https://guide.kangjianai.cn/daily`
- 本 skill **不内置网站代码**；以下集成步骤仅在你需要「自动发布到自己的站点」时启用，否则跳过（见上文「独立使用」）。

### 目录结构

```
apps/ai-programming-guide/
├── content/daily/          ← 日报 Markdown 文件（YYYY-MM-DD.md）
├── src/data/
│   └── dailyDigests.generated.js  ← 自动生成，勿手动修改
└── scripts/
    ├── update-daily-digest.mjs    ← 读 content/daily/ → 更新数据文件
    ├── publish-wechat-daily.mjs   ← 发布到微信公众号
    ├── daily-deploy.sh            ← 一键：更新+构建+rsync
    └── daily-service.mjs          ← 后台监听服务（文件变更自动部署）
```

### 阶段 4 执行命令

```bash
# 写入日报文件（由 Write 工具完成）
# <APP_DIR>/content/daily/YYYY-MM-DD.md

# 更新网站数据
APP_DIR="<你的仓库>/apps/ai-programming-guide"   # 改成你的绝对路径
DATE=$(date +%Y-%m-%d)
node "$APP_DIR/scripts/update-daily-digest.mjs" --date "$DATE"
```

### 手动部署

```bash
cd "$APP_DIR"           # 你的 apps/ai-programming-guide 绝对路径
pnpm daily:deploy       # 更新数据 → 构建 → rsync 到阿里云 ECS
```

### 自动部署（后台服务）

```bash
pnpm daily:service:install   # 安装 launchd 开机自启
# 之后每次 Cowork 写入新日报，自动触发构建部署
```

### 微信公众号发布

```bash
# 需先在 .env 配置 WX_THUMB_MEDIA_ID（封面图 media_id）
pnpm daily:publish --file content/daily/YYYY-MM-DD.md
```

---

## 适配到其他项目

如果要把本技能适配到新项目，需要：

1. 在项目中创建 `content/daily/` 目录
2. 复制 `scripts/update-daily-digest.mjs`（通用脚本，无项目耦合）
3. 修改 SKILL.md 中 `<APP_DIR>` 为新项目路径
4. 根据部署方式调整 `daily-deploy.sh`

---

## npm 脚本速查

| 命令 | 作用 |
|------|------|
| `pnpm daily:update` | 全量同步 `content/daily/` → `dailyDigests.generated.js` |
| `pnpm daily:deploy` | 更新数据 + 构建 + rsync 部署 |
| `pnpm daily:publish` | 发布到微信公众号 |
| `pnpm daily:service` | 启动文件监听守护进程 |
| `pnpm daily:service:install` | 安装为 Mac launchd 开机自启 |
