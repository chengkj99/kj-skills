---
name: course-scraper
description: >-
  抓取课程/网页正文和图片并存为结构化 Markdown（图片默认下载到本地 _assets/ 并改写链接），
  可选翻译成中英双语（中文在前，英文原文用引用块紧随）。
  支持两种模式：①「单课程平台模式」——自动登录课程平台（如 Skilljar），遍历侧边栏课时（用 scripts/scrape.py）；
  ②「链接清单模式」——给一份含许多异构链接的清单（导航页、资源合集、Markdown 链接表），逐链 Playwright 渲染抓取
  （用 scripts/fetch_links.py），带 trafilatura→markdownify→WebFetch 反爬兜底阶梯与质量标记。
  触发词：抓取课程、course scraper、scrape course、课程抓取、帮我把课程内容抓下来、把网页课程内容保存下来、
  课程抓取翻译、把课程翻译成中文、抓取这些链接、把清单里的链接内容抓下来、批量抓网页、抓取资源合集。
---

# Course Scraper — 课程抓取 & 双语翻译

从在线课程平台抓取所有课时文字内容与图片，存为结构化 Markdown，并翻译成中英对照格式。

---

## 适用场景

- 用户提供一个课程 URL（如 Skilljar、LMS 类平台），想把内容本地存档 → **单课程平台模式**
- 用户提供一份**链接清单/导航页/资源合集**（几十条跨域链接），想把这些链接的正文都抓下来 → **链接清单模式**
- 需要将英文内容翻译成中英双语对照版本
- 课程需要账号登录才能访问
- 需要把网页/PDF/课程里的图片一并本地归档，避免 Markdown 依赖远程图片

---

## 图片抓取规则（默认开启）

两个脚本都必须把图片作为正文资产的一部分处理：

- 图片保存位置：每篇文章/课时旁边的 `_assets/<文件slug>/`
- Markdown 写法：正文里的远程图片链接改成本地相对路径，例如 `![](./_assets/xx/01-image.png)` 或 `![](_assets/xx/01-image.png)`
- 如果正文提取器没有保留图片位置，脚本会在文末追加 `## 图片 / Images` 区块，至少保证图片不丢。
- 文件头或报告中记录图片数量：`图片 / Images: 已下载数/候选数`
- 跳过 `data:`、`blob:` 与明显小图标；下载失败不阻塞正文抓取，但必须在报告中体现下载数量。

> 经验教训：早期版本只抓正文，`scrape.py` 甚至只取 `inner_text()`，会把课程截图、流程图、UI 图全部丢掉。后续任何抓取都要把“图片本地化”作为验收项。

---

## 先判别模式（最重要）

拿到需求后，**第一步判断属于哪种模式**，不要默认套单课程逻辑：

| 信号 | 模式 | 用哪个脚本 |
|------|------|-----------|
| 一个课程站点、登录后有侧边栏课时列表（Skilljar/LMS） | **单课程平台模式** | `scripts/scrape.py` |
| 一份 Markdown/文档里列了**许多不同域名**的链接（资源清单、导航页、合集） | **链接清单模式** | `scripts/fetch_links.py` |

> 经验教训：曾有用户拿「一份 80+ 条异构链接的资源清单」触发本技能，若硬套单课程登录逻辑会完全跑偏。
> 链接清单 ≠ 一门课程，必须走 `fetch_links.py` 逐链抓取。

---

## 信息收集（执行前必须确认）

在运行任何脚本之前，先向用户确认以下信息：

1. **抓取范围**：
   - 单课程模式 → 课程首个课时 URL
   - 链接清单模式 → 清单文件路径 + **抓哪些部分**（清单常含视频/付费/无关链接，需圈定范围；YouTube 等视频无正文，应排除或单独说明）
2. **登录凭据**：账号邮箱 + 密码（若平台需要登录）。无凭据的登录墙链接（如 OpenAI Academy 走 OAuth）须事先说明如何处理：放弃 / 用户手动登录粘贴 / 提供凭据。
3. **保存位置**：
   - 若当前项目存在 `raw/papers/` 目录 → 默认保存到 `raw/papers/<课程名>/`
   - 若不存在 → 询问用户希望保存到哪里，或建议合适路径
4. **是否需要翻译**：默认翻译为中英双语；用户可选择跳过翻译。**注意翻译体量**：大批量页面（数十万字符）翻译会跨很多轮、消耗很大，应先与用户确认范围/优先级，分批逐文件写盘。

---

## 执行流程（单课程平台模式）

### 第一步：环境检查

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('ok')" 2>/dev/null || echo "need_install"
```

如果输出 `need_install`，先安装：

```bash
pip3 install playwright && python3 -m playwright install chromium
```

### 第二步：运行抓取脚本

使用技能内置脚本 `scripts/scrape.py` 执行抓取。调用方式：

```bash
python3 <skill_dir>/scripts/scrape.py \
  --url "<课程首个课时 URL>" \
  --email "<账号邮箱>" \
  --password "<密码>" \
  --output "<输出目录绝对路径>"
```

脚本会自动：
- 识别平台类型（目前支持 Skilljar；其他平台见下方「其他平台」章节）
- 登录账号
- 从侧边栏收集所有课时链接
- 逐一抓取每个课时的正文内容
- 下载课时正文区域图片到 `_assets/<课时slug>/`，并在 Markdown 中追加本地图片引用
- 按顺序保存为 `01-<slug>.md`、`02-<slug>.md` …
- 生成 `00-index.md` 索引

### 第三步：翻译为双语格式

抓取完成后，对输出目录中每个非索引的 `.md` 文件进行翻译。

**双语格式规范**：
- 章节标题：`英文标题 / 中文标题`
- 正文段落：先写中文译文，紧接着英文原文放在 `>` 引用块
- 代码块、命令保持原样不翻译
- 示例：

```markdown
## Installing Claude Code / 安装 Claude Code

安装 Claude Code 非常简单，无论你想在终端、网页还是 IDE 中使用。

> Claude Code is simple to install whether you want to use it in your terminal, on the web, or in your IDE.
```

逐文件翻译，翻译完成后直接覆写原文件（原英文内容保留在引用块中）。

### 第四步：输出确认

完成后向用户报告：
- 保存路径
- 抓取的课时数量及文件名列表
- 是否完成翻译

---

## 执行流程（链接清单模式）

### 第一步：环境检查 + 安装提取库

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('ok')" 2>/dev/null || echo "need_install"
python3 -c "import trafilatura, markdownify; print('extract ok')" 2>/dev/null || echo "need_extract"
```

缺什么装什么：

```bash
pip3 install playwright trafilatura markdownify && python3 -m playwright install chromium
```

- **trafilatura**：从渲染后的 HTML 中提取**主内容**为 Markdown（去导航/页脚/广告），效果最好。
- **markdownify**：trafilatura 提取过薄时的兜底（整页转换，可能带噪声）。

### 第二步：圈定范围

清单里常混着**视频（YouTube）、登录墙、付费墙、无关导航**链接。抓之前先和用户确认抓哪些分节；
视频类无正文，应排除或单独说明。无凭据的登录墙链接（OAuth）默认跳过并记录。

### 第三步：运行逐链抓取脚本

```bash
python3 <skill_dir>/scripts/fetch_links.py \
  --links "<清单文件路径>" \
  --output "<输出目录绝对路径>" \
  [--subdir 01-official-docs] [--limit N]
```

脚本会：解析清单里的链接（Markdown 表格自动取标题）→ 逐个 Playwright 渲染 → trafilatura 提取
→ markdownify 兜底 → 下载可见正文图片并本地化 Markdown 图片链接 → 存为 `01-<slug>.md` …
→ 写 `_fetch_report.json`（含每条 ok/thin/error 与图片下载数量）。

> 大清单建议 `run_in_background` 跑（几十页约 5–8 分钟），完成后读 `_fetch_report.json` 核对。

### 第四步：反爬兜底阶梯（关键）

脚本跑完后，对报告里 **THIN / ERROR** 的链接逐条兜底，**阶梯顺序**：

1. **Playwright 重试**：改 `wait_until="load"` + 加长等待；跨域 301 跳转时换跳转后的 URL 重试。
2. **WebFetch 工具兜底**：仍失败则用 `WebFetch` 抓取（它走另一条抓取路径，常能绕过 Cloudflare/JS 营销页）。
   ⚠️ **WebFetch 会用小模型「摘要」内容，不是逐字原文**——只能当兜底，且必须在文件头标注
   `抓取方式: WebFetch 兜底；为可读提取，非逐字原文`，不可冒充原文存档。
3. **仍拿不到**：按下方「质量标记」记为 ⚠️ 或 ❌，写一个说明页（标注原因 + 原链接 + 可替代的官方页），不要留垃圾内容。

常见失败与处置：

| 现象 | 含义 | 处置 |
|------|------|------|
| markdownify-fallback 且字符数巨大（几十万） | 纯 JS 页，trafilatura 提不出，dump 了 CSS/JS | 判为失败，改 WebFetch；不行就写说明页（⚠️） |
| 301 跨域跳转 | 站点迁移（如 www→cn 子站） | 用跳转后 URL 重抓 |
| 404 | 链接已失效 | 写说明页（❌），建议用户搜标题找新址 |
| 403 / "security verification" / 极短正文 | Cloudflare/反爬 或营销页 | WebFetch 兜底；标注 ◐ 非逐字 |
| 内容很短但页面正常 | 付费/预览墙 | 取公开预览部分，标注付费墙 |

### 第五步：生成索引 + 质量标记

写 `00-index.md`，按分节列出每个文件及**质量标记**，让用户一眼看清哪些可信、哪些要复核：

> ✅ Playwright 完整原文 ｜ ◐ WebFetch 兜底（非逐字，已在文件头标注）｜ ⚠️ 部分失败 ｜ ❌ 链接失效 ｜ ⏳ 待处理（如登录墙）

同时检查图片本地化：

```bash
rg -n '!\[[^\]]*\]\(https?://' <输出目录> --glob '*.md'
```

若有输出，说明仍有远程图片链接，需要补下载或在文件头标注原因。

### 第六步：翻译（可选，见下方「翻译为双语格式」）

---

## Skilljar 平台登录说明

Skilljar 的登录流程与一般平台不同：

1. 访问 `<课程根 URL>?next=<目标路径>` 会被重定向到 `https://accounts.skilljar.com/accounts/login/`
2. 登录表单字段：`#id_login`（邮箱）、`#id_password`（密码）
3. 触发登录跳转的方式：直接访问 `<BASE>/auth/login?next=<课程路径>`
4. 登录成功后跳回课程页面，侧边栏出现所有课时链接（`a[href*="/<course-slug>/数字"]`）

---

## 其他平台（无内置支持时的处理）

如果平台不是 Skilljar，按如下步骤降级处理：

1. **先尝试无登录直接访问**：如果内容可见，跳过登录步骤
2. **查找登录入口**：在页面上查找包含 `sign in`、`log in`、`login` 文字的链接并点击
3. **查找登录表单**：找 `input[type="email"]` 和 `input[type="password"]`，填写凭据后提交
4. 登录失败时，告知用户并请求他们提供正确的登录页 URL 或额外说明

---

## 上下文窗口保护

翻译内容较多时，逐文件处理而不是一次性加载所有文件。每翻译完一个文件立即写入磁盘，避免上下文过载。

---

## 参考文件

- [`scripts/scrape.py`](scripts/scrape.py) — **单课程平台模式**：Playwright 抓取脚本（支持 Skilljar 登录 + 课时遍历）
- [`scripts/fetch_links.py`](scripts/fetch_links.py) — **链接清单模式**：逐链 Playwright 渲染 + trafilatura 提取 + markdownify 兜底，输出报告 JSON
- [`references/platform-notes.md`](references/platform-notes.md) — 各平台登录行为 + 反爬站点处置备注
