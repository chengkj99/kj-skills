---
name: course-scraper
description: >-
  根据用户提供的课程链接，自动登录课程平台（支持 Skilljar 等需要账号的平台），
  用 Playwright 抓取全部课时内容，按课时保存为独立 Markdown 文件，生成索引，
  最后翻译成中英双语格式（中文在前，英文原文用引用块紧随）。
  触发词：抓取课程、course scraper、scrape course、课程抓取、帮我把课程内容抓下来、
  把网页课程内容保存下来、课程抓取翻译、把课程翻译成中文。
---

# Course Scraper — 课程抓取 & 双语翻译

从在线课程平台抓取所有课时文字内容，存为结构化 Markdown，并翻译成中英对照格式。

---

## 适用场景

- 用户提供一个课程 URL（如 Skilljar、LMS 类平台），想把内容本地存档
- 需要将英文课程翻译成中英双语对照版本
- 课程需要账号登录才能访问

---

## 信息收集（执行前必须确认）

在运行任何脚本之前，先向用户确认以下信息：

1. **课程 URL**：目标课程的链接（如果用户已提供，直接使用）
2. **登录凭据**：账号邮箱 + 密码（若平台需要登录）
3. **保存位置**：
   - 若当前项目存在 `raw/papers/` 目录 → 默认保存到 `raw/papers/<课程名>/`
   - 若不存在 → 询问用户希望保存到哪里，或建议合适路径
4. **是否需要翻译**：默认翻译为中英双语；用户可选择跳过翻译

---

## 执行流程

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

- [`scripts/scrape.py`](scripts/scrape.py) — Playwright 抓取脚本（支持 Skilljar 登录 + 课时遍历）
- [`references/platform-notes.md`](references/platform-notes.md) — 各平台登录行为备注
