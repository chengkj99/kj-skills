# 格式化示例

## 表格：缺分隔行（Obsidian 不渲染）

**Before**

```markdown
| **症状** | **解决方案** |
| 权限弹窗频繁 | /permissions 白名单常用命令 |
```

**After**

```markdown
| **症状** | **解决方案** |
| --- | --- |
| 权限弹窗频繁 | /permissions 白名单常用命令 |
```

## 标题：加粗伪标题

**Before**

```markdown
**第三章 核心概念**

**3.1 Agent Loop**
```

**After**

```markdown
# 第三章 核心概念

## 3.1 Agent Loop
```

## 代码：逐行引用 → 围栏

**Before**

```markdown
> curl -fsSL https://claude.ai/install.sh | bash
>
> claude --version
```

**After**

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

## 提示：多行 Claude 输入

**Before**

```markdown
> 用 Node.js + Express 创建一个 Todo REST API，
包含增删改查接口。
```

**After**

```bash
> 用 Node.js + Express 创建一个 Todo REST API，
> 包含增删改查接口。
```

## 提示框：HTML 表格 → 引用块

**Before**

```html
<table><tr><td><strong>新手建议</strong><p>先充值约 20 美元…</p></td></tr></table>
```

**After**

```markdown
> **新手建议**
>
> 先充值约 20 美元 API 额度，用自己真实工作流评估 1–2 周，再决定是否订阅 Max。
```
