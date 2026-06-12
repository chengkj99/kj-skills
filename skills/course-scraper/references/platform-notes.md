# 平台登录行为备注

## Skilljar

- **登录入口**：不是直接访问 `/users/sign_in`，而是通过 `<base>/auth/login?next=<course_path>` 触发跳转
- **登录域**：跳转后进入 `accounts.skilljar.com/accounts/login/`（与课程主域不同）
- **表单字段**：`#id_login`（邮箱）、`#id_password`（密码）
- **课时链接特征**：`/claude-code-101/469788` 这类格式，路径末尾为纯数字
- **侧边栏**：登录后课程页面侧边栏会列出所有课时的 `<a href>` 链接
- **Next 按钮**：文字为"Next"，链接格式与课时链接相同

## 通用 LMS 平台

- 先查找带 `sign in` / `log in` 文字的链接，点击后再查找表单
- 常见表单字段：`input[type="email"]`、`input[type="password"]`
- 提交按钮：`button[type="submit"]` 或 `input[type="submit"]`

## Teachable

- 登录 URL：`/sign_in`
- 表单字段：`#email`、`#password`

## Thinkific

- 登录 URL：`/users/sign_in`
- 表单字段：`#user_email`、`#user_password`

## 注意事项

- 某些平台使用 OAuth / SSO，无法直接填表单登录，需要用户手动登录后导出 Cookie
- 视频课时通常没有可抓取的文字内容，脚本会标注"视频课时"并跳过
- 部分平台使用 Shadow DOM 渲染内容，`inner_text()` 可能需要配合 `frame` 切换

---

# 链接清单模式：反爬站点处置备注

（来自实战经验，配合 `scripts/fetch_links.py` 的兜底阶梯使用）

## 各类站点抓取难度

| 站点类型 | Playwright+trafilatura | 处置 |
|---------|------------------------|------|
| 官方文档站（如 developers.openai.com，Next.js SSR） | ✅ 通常完美，逐字原文 | 直接用 |
| GitHub 仓库/Releases 页 | ✅ README 可提取 | 直接用 |
| 普通技术博客（FreeCodeCamp、个人站、Substack 公开页） | ✅ 多数可提取 | 直接用 |
| **Cloudflare 反爬**（DataCamp、部分 SaaS 博客） | ❌ 返回 "security verification" 拦截页 | WebFetch 兜底（常能绕过） |
| **登录墙**（Medium 会员文、dev.to 偶发） | ❌ 导航被重定向中断 | WebFetch 兜底；仍不行写说明页 |
| **纯 JS 营销落地页**（openai.com/codex/ 这类） | ❌ trafilatura 提不出，markdownify 会 dump CSS/JS（文件巨大但全是噪声） | WebFetch（可能 403）；不行写说明页 ⚠️ |
| **付费墙**（付费 Substack/Newsletter） | ◐ 只得公开预览片段 | 取预览，标注付费墙 |
| **已失效链接** | 404 | 写说明页 ❌，建议用户按标题搜新址 |

## 关键经验

- **WebFetch ≠ 原文**：它用小模型把页面**摘要**后返回，长文会被大幅压缩。只能当 Playwright 失败时的兜底，
  且必须在文件头明确标注「非逐字原文」，否则会被误当原文存档。
- **301 跨域跳转**：WebFetch 遇到跨 host 跳转会**返回跳转 URL 让你再发一次**（不自动跟随）；用新 URL 重抓。
- **markdownify 兜底产物异常大**（几十万字符）通常是垃圾（整页 CSS/JS），应判为失败而非成功。
- **质量标记写进索引**：✅ 完整原文 / ◐ WebFetch 非逐字 / ⚠️ 部分失败 / ❌ 失效 / ⏳ 待处理，让用户一眼分辨可信度。
