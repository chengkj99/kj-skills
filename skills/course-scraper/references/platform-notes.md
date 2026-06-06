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
