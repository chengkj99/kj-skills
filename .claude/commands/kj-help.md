---
description: 自动扫描并列出 kj-skills 插件内所有 skill 的用途与 skills/ 下的路径
---

扫描本插件 `skills/` 目录下的所有 skill，动态生成清单（不要使用任何写死的列表）。

执行步骤：

1. 运行以下命令，逐个读取每个 skill 的 `description`：

   ```bash
   for f in skills/*/SKILL.md; do
     d=$(basename "$(dirname "$f")")
     desc=$(awk '/^description:/{flag=1; sub(/^description:[ ]*/,""); print; next} flag&&/^[a-zA-Z_-]+:/{exit} flag{print}' "$f" | tr '\n' ' ' | sed 's/^[">|-]*[ ]*//')
     echo "$d :: $desc"
   done
   ```

2. 把结果整理成 Markdown 表格，按目录名排序，`用途` 取 description 的核心意图，精简到一句话（约 30–40 字）：

   | 目录 | 用途 |
   |------|------|

3. 表格下方追加一行提示：「请用 **Read** 打开对应目录的 `SKILL.md` 再执行；若某 skill 带 `disable-model-invocation`，需用户显式 @ 才会触发，以各 SKILL frontmatter 为准。」

4. 若发现异常（某目录缺 `SKILL.md`、`name` 与目录名不一致、描述为空），在表格后用一行 ⚠️ 单独指出，便于维护。
