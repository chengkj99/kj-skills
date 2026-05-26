# Commit 说明模式参考

根据 `git diff` 输出匹配下列模式，生成合适的 Conventional Commits 标题。

## 按变更类型

### 依赖更新

**特征**：`package.json`、`yarn.lock`、`package-lock.json`、`pnpm-lock.yaml` 等

```text
fix(deps): update <package> to <version>
fix(deps): upgrade handlebars to 4.7.9 for security fix
```

安全修复可加正文：

```text
Fixes GHSA-xxxx-xxxx-xxxx
```

### 新功能

**特征**：新文件、新函数、新组件、新 API

```text
feat(<scope>): add <description>
feat(auth): add OAuth2 login support
feat(ui): create UserCard component
```

### Bug 修复

**特征**：修正既有逻辑错误

```text
fix(<scope>): <what-was-fixed>
fix(login): resolve redirect loop on auth failure
```

### 重构

**特征**：结构调整，行为不变

```text
refactor(<scope>): <what-was-refactored>
refactor(auth): extract token validation to separate module
```

### 文档

**特征**：README、docs、注释

```text
docs: update installation instructions
docs(api): document new endpoints
```

### 格式 / 风格

**特征**：lint、prettier、仅空白

```text
style: fix linting errors
style: format code with prettier
```

### 测试

**特征**：测试文件增删改

```text
test(<scope>): add unit tests for login flow
```

### 配置 / 杂项

**特征**：CI、构建配置、工具链

```text
chore(ci): add deploy workflow
chore(config): update eslint configuration
```

## Scope 推断

| 路径模式 | 建议 scope |
|----------|------------|
| `src/components/**` | `ui` 或组件名 |
| `src/api/**` | `api` |
| `src/utils/**` | `utils` |
| `package.json` | `deps` |
| `.github/**` | `ci` |
| `skills/**` | `skills` 或具体 skill 名 |
| 仓库根目录零散文件 | 可省略 scope |

## 长度与正文

- **标题**：尽量 50–72 字符内
- **正文**：每行约 72 字符换行；写清动机与影响范围
- **破坏性变更**：`feat(api)!: ...` 或正文 `BREAKING CHANGE: ...`

## 完整示例

```text
fix(deps): upgrade handlebars to 4.7.9
```

```text
feat(auth): add OAuth2 login support

- Implement Google OAuth provider
- Add session management

Closes #123
```

```text
feat(api)!: change user endpoint response format

BREAKING CHANGE: 响应由扁平结构改为嵌套对象，客户端需同步升级。
```
