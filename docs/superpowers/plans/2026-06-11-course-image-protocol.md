# Course Image Protocol 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 SVG 图片生成规范集成到 course-generator 和 course-campaign，让两个 skill 能自动生成流程图/对比图 SVG、保留描述注释、并在批量写课后输出排版规范化的图片完成度报告。

**Architecture:** 新建 `image-protocol.md` 作为协议真相源；course-generator 写完章节后内联生成 SVG（Step 3.5）；course-campaign 全部章节完成后规范化 PNG 引用并输出完成度报告（Step E）。

**Tech Stack:** Markdown skill 文件，SVG（手写），Bash grep/sed（用于 Step E PNG 规范化）

**Spec:** `docs/superpowers/specs/2026-06-11-course-image-protocol-design.md`

---

## 文件变更地图

| 文件 | 操作 | 位置 |
|------|------|------|
| `skills/course-generator/references/image-protocol.md` | 新建 | 全文 |
| `skills/course-generator/references/chapter-blueprint.md` | 修改 | `## 视觉元素指南` 节 |
| `skills/course-generator/SKILL.md` | 修改 | Step 2 之后插入 Step 3.5 |
| `skills/course-campaign/SKILL.md` | 修改 | Step D 之后插入 Step E |

---

## Task 1：新建 `image-protocol.md`

**Files:**
- Create: `skills/course-generator/references/image-protocol.md`

- [ ] **Step 1: 写入文件**

```bash
cat > /Users/chengkangjian/work/kj-skills/skills/course-generator/references/image-protocol.md << 'EOF'
# 图片生成协议（image-protocol）

> course-generator 和 course-campaign 共同遵守的图片处理规范。

## 1. 占位类型与处理方式

| 占位类型 | 能否自动生成 | 处理方式 |
|---------|------------|---------|
| `[流程图]` | ✅ SVG | course-generator Step 3.5 内联生成 |
| `[对比图]` | ✅ SVG | course-generator Step 3.5 内联生成 |
| `[截图]` | ❌ 手动 | 保留注释，录课时补 |
| `[录屏建议]` | ❌ 手动 | 保留注释，录课时执行 |

## 2. A 方案：注释与图片引用并存

插入图片后**不删原有注释**，二者相邻写在同一位置：

```markdown
<!-- [流程图] 描述：三层 CLAUDE.md 加载顺序... -->
![CLAUDE.md 层级示意图](../../../../assets/lessons-claudecode/cc005-claudemd-hierarchy.svg)
```

**原因**：注释是描述的真相源。图片丢失或需重新生成时，注释里有完整描述，无需翻历史记录。

## 3. SVG 文件命名与存放

- **命名**：`<课程编号小写>-<slug>.svg`
  - 示例：`cc005-claudemd-hierarchy.svg`
  - slug 从注释描述中提炼，2-4 个英文词，用 `-` 连接
- **存放**：`assets/lessons-claudecode/`（或当前课程对应的 assets 目录）

## 4. SVG 质量要求

- **字体**：`font-family="'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"`
- **画布**：`viewBox="0 0 620 480"` width="620" height="480"
- **背景**：`fill="#FAFAFA"` `rx="12"`
- **节点**：浅色背景 + 深色左侧色条（`width="6"` `rx="3"`），圆角 `rx="10"`
- **文字大小**：标题 14-15px，正文 12-13px，说明 11px
- **箭头**：每条连线必须有文字标注（如「叠加」「触发」「返回」）
- **验证**：用 `open` 命令本地预览，确认渲染正常后再插入正文

## 5. SVG 生成提示词模板

执行 Step 3.5 时，将以下提示词与描述注释内容合并发给自己：

```
你是一个 SVG 技术图表生成专家。根据描述生成一张可在浏览器直接渲染的 SVG 图表。

## 固定规范（每张图必须遵守）
- 画布：viewBox="0 0 620 480"，width="620" height="480"
- 背景：fill="#FAFAFA" rx="12"
- 字体：font-family="'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
- 文字大小：标题 14-15px，正文 12-13px，说明 11px
- 节点：浅色背景 + 深色左侧色条（宽 6px），圆角 rx="10"
- 箭头：每条连线必须有文字标注
- 输出：只输出 <svg>...</svg> 完整代码，不加任何其他文字

## 图表类型识别
- 层级/加载顺序 → 纵向堆叠矩形 + 虚线箭头
- 流程/决策 → 菱形判断 + 矩形步骤 + 实线箭头
- 对比/横向比较 → 左右分栏，顶部标题色块区分
- 连接关系/拓扑 → 中心节点 + 放射状连线

## 配色方案
第一层：背景 #E8F4FD / 边框 #4A9FD4
第二层：背景 #EAF7EE / 边框 #52A96A
第三层：背景 #FEF3E8 / 边框 #E08A3A
中性底栏：#F0F0F0

描述：{把 <!-- [流程图] 描述：... --> 里的描述文本填在这里}
```

## 6. 排版一致性约定

课程文件中 SVG 与 PNG 混排时，统一展示宽度为 **620px**：

- SVG：已由 `width="620"` 保证，天然一致，无需修改
- PNG 截图：**禁止**使用 Markdown `![]()` 语法，改用 HTML `<img>` 标签：

```html
<!-- [截图] 描述：... -->
<img src="../../../../assets/lessons-claudecode/xxx.png" width="620" alt="描述文字" />
```

`course-campaign` Step E1 负责将已有 `![](*.png)` 批量规范化为此格式。
EOF
```

- [ ] **Step 2: 验证 6 个章节均已写入**

```bash
grep -c "^## " /Users/chengkangjian/work/kj-skills/skills/course-generator/references/image-protocol.md
```

预期输出：`6`

- [ ] **Step 3: 提交**

```bash
cd /Users/chengkangjian/work/kj-skills
git add skills/course-generator/references/image-protocol.md
git commit -m "feat(course-generator): add image-protocol.md — SVG generation protocol"
```

---

## Task 2：更新 `chapter-blueprint.md` 视觉元素指南

**Files:**
- Modify: `skills/course-generator/references/chapter-blueprint.md`（`## 视觉元素指南` 节）

- [ ] **Step 1: 确认当前「核心原则」第3条的位置**

```bash
grep -n "无法由 AI 生成\|代码块直接写进正文" \
  /Users/chengkangjian/work/kj-skills/skills/course-generator/references/chapter-blueprint.md
```

预期输出：含「截图 / 流程图 / 录屏无法由 AI 生成」的行号。

- [ ] **Step 2: 替换「核心原则」第3条**

将：
```
- 代码块直接写进正文；截图 / 流程图 / 录屏无法由 AI 生成，用**占位标记**精确描述，供用户后续补充。
```

替换为：
```
- 代码块直接写进正文。`[流程图]` 和 `[对比图]` 由 AI 在 Step 3.5 自动生成 SVG；`[截图]` 和 `[录屏建议]` 用占位标记保留，录课时手动补充。完整协议见 [image-protocol.md](image-protocol.md)。
```

用 Edit 工具执行此替换。

- [ ] **Step 3: 验证链接目标存在**

```bash
ls /Users/chengkangjian/work/kj-skills/skills/course-generator/references/image-protocol.md
```

预期输出：文件路径（Task 1 已创建）。

- [ ] **Step 4: 验证修改结果**

```bash
grep -A2 "image-protocol" \
  /Users/chengkangjian/work/kj-skills/skills/course-generator/references/chapter-blueprint.md
```

预期输出：包含 `[image-protocol.md](image-protocol.md)` 的行。

- [ ] **Step 5: 提交**

```bash
cd /Users/chengkangjian/work/kj-skills
git add skills/course-generator/references/chapter-blueprint.md
git commit -m "feat(course-generator): update chapter-blueprint visual guide — SVG now auto-generated"
```

---

## Task 3：在 `course-generator/SKILL.md` 新增 Step 3.5

**Files:**
- Modify: `skills/course-generator/SKILL.md`

- [ ] **Step 1: 确认插入位置**

```bash
grep -n "第 3 步\|Step 3\|第 2 步\|Step 2\|质量门禁" \
  /Users/chengkangjian/work/kj-skills/skills/course-generator/SKILL.md
```

预期输出：找到「第 2 步：写正文」和「第 3 步：过质量门禁」的行号，Step 3.5 插在两者之间。

- [ ] **Step 2: 插入 Step 3.5**

在「### 第 3 步：过质量门禁」标题**之前**，用 Edit 工具插入以下内容：

```markdown
### 第 3.5 步：生成可自动化的视觉元素（SVG）

打开 [references/image-protocol.md](references/image-protocol.md)，扫描本章正文中所有 `<!-- [流程图] -->` 和 `<!-- [对比图] -->` 占位，逐一处理：

1. 取出注释里的**描述文本**，填入 image-protocol.md 第 5 节的提示词模板。
2. 按模板生成 SVG 代码，写入 `assets/lessons-claudecode/<编号>-<slug>.svg`（命名规则见 image-protocol.md 第 3 节）。
3. 用 `open` 命令本地预览，确认渲染正常。
4. 按 **A 方案**在注释下方紧接插入图片引用（**保留注释，不删**）：
   ```markdown
   <!-- [流程图] 描述：... -->
   ![alt 文字](../../../../assets/lessons-claudecode/xxx.svg)
   ```
5. `[截图]` 和 `[录屏建议]` **原样保留**，不处理。

> 每章通常 1-2 张，不会显著影响写章节节奏。若描述不够清晰导致 SVG 难以准确表达，告知用户并跳过该张（保留占位）。

```

- [ ] **Step 3: 验证步骤顺序正确**

```bash
grep -n "第 [0-9.]*步\|Step [0-9.]" \
  /Users/chengkangjian/work/kj-skills/skills/course-generator/SKILL.md
```

预期输出：步骤顺序为 0 → 1 → 2 → 3.5 → 3 → 4，无乱序。

- [ ] **Step 4: 提交**

```bash
cd /Users/chengkangjian/work/kj-skills
git add skills/course-generator/SKILL.md
git commit -m "feat(course-generator): add Step 3.5 — inline SVG generation for flowcharts"
```

---

## Task 4：在 `course-campaign/SKILL.md` 新增 Step E

**Files:**
- Modify: `skills/course-campaign/SKILL.md`

- [ ] **Step 1: 确认插入位置**

```bash
grep -n "Step D\|全部章节\|收尾\|结束" \
  /Users/chengkangjian/work/kj-skills/skills/course-campaign/SKILL.md
```

预期输出：找到 Step D 和「全部章节 done 后」收尾逻辑的行号，Step E 插在收尾总结之前。

- [ ] **Step 2: 插入 Step E**

在「全部章节 `done` 后，给一句收尾总结」**之前**，用 Edit 工具插入以下内容：

```markdown
### Step E：图片规范化 + 完成度审计（全部章节 done 后执行一次）

**E1. 规范化混排图片尺寸**

扫描本次 campaign 涉及的所有章节文件，将 Markdown 语法的 PNG 引用替换为统一宽度的 HTML 标签：

```bash
# 找出所有 Markdown 图片语法引用 PNG 的行
grep -rn "!\[.*\](.*\.png)" <输出目录>
```

对每处匹配，将：
```markdown
![alt 文字](path/to/image.png)
```
改写为：
```html
<img src="path/to/image.png" width="620" alt="alt 文字" />
```

SVG 引用（`![](*.svg)`）**不处理**，已由 `width="620"` 属性保证一致。

**E2. 输出完成度报告**

统计并输出以下清单（即录课行动清单）：

```
📊 图片完成度报告
✅ SVG 已生成：N 张
🖼️ PNG 已规范化：N 处（统一为 width=620）
📷 截图待补：N 处
   - CC-007:37 — Plan Mode 界面截图
   - CC-009:133 — macOS 通知弹窗
   ...
🎬 录屏待录：N 处
```

```

- [ ] **Step 3: 验证 Step E 已插入且在收尾总结之前**

```bash
grep -n "Step E\|收尾总结\|共写了几章" \
  /Users/chengkangjian/work/kj-skills/skills/course-campaign/SKILL.md
```

预期输出：Step E 的行号小于收尾总结的行号。

- [ ] **Step 4: 提交**

```bash
cd /Users/chengkangjian/work/kj-skills
git add skills/course-campaign/SKILL.md
git commit -m "feat(course-campaign): add Step E — image normalization and completion audit"
```

---

## Task 5：端到端冒烟验证

- [ ] **Step 1: 验证 4 个文件均已落地**

```bash
ls /Users/chengkangjian/work/kj-skills/skills/course-generator/references/image-protocol.md
grep -c "image-protocol" /Users/chengkangjian/work/kj-skills/skills/course-generator/references/chapter-blueprint.md
grep -c "第 3.5 步" /Users/chengkangjian/work/kj-skills/skills/course-generator/SKILL.md
grep -c "Step E" /Users/chengkangjian/work/kj-skills/skills/course-campaign/SKILL.md
```

预期输出：4 行均不为 0。

- [ ] **Step 2: 验证交叉引用一致（image-protocol.md 节号）**

```bash
grep -n "^## " /Users/chengkangjian/work/kj-skills/skills/course-generator/references/image-protocol.md
```

预期输出：节号 1-6 顺序完整，无跳号。

- [ ] **Step 3: 确认 git log 包含 4 次提交**

```bash
cd /Users/chengkangjian/work/kj-skills && git log --oneline -5
```

预期输出：最近 4 条 commit 分别对应 Task 1-4。
