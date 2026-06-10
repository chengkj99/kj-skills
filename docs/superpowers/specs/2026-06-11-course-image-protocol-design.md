# 设计文档：课程图片生成协议集成到 course-generator 与 course-campaign

**日期**：2026-06-11  
**状态**：待实现  
**涉及文件**：
- `skills/course-generator/references/image-protocol.md`（新建）
- `skills/course-generator/references/chapter-blueprint.md`（更新视觉元素指南）
- `skills/course-generator/SKILL.md`（新增 Step 3.5）
- `skills/course-campaign/SKILL.md`（新增 Step E）

---

## 背景与问题

`chapter-blueprint.md` 的视觉元素指南写道「截图/流程图/录屏无法由 AI 生成，用占位标记」。这条规则已经过时：

- `[流程图]` 和 `[对比图]` 可以直接生成 SVG——精确、可控、无需 API key。
- `[截图]` 和 `[录屏建议]` 仍需手动。

同时存在一个管理问题：当图片生成后替换了原始注释，描述就永久丢失，之后无法重新生成。

---

## 设计目标

1. `course-generator` 写完章节后，自动为 `[流程图]`/`[对比图]` 生成 SVG 并插入文件。
2. 描述注释永不被删除（A方案：注释 + 图片引用并存）。
3. 图片生成规范集中在一个 reference 文件，两个 skill 共用。
4. `course-campaign` 收尾时输出一张图片完成度报告，作为录课行动清单。

---

## 架构

### 新建：`course-generator/references/image-protocol.md`

课程图片生成的完整协议，内容：

**1. 占位类型与处理方式**

| 占位类型 | 能否自动生成 | 处理方式 |
|---------|------------|---------|
| `[流程图]` | ✅ SVG | course-generator 内联生成 |
| `[对比图]` | ✅ SVG | course-generator 内联生成 |
| `[截图]` | ❌ 手动 | 保留注释，录课时补 |
| `[录屏建议]` | ❌ 手动 | 保留注释，录课时执行 |

**2. A方案约定：注释与图片引用并存**

插入图片后不删原有注释，二者相邻：

```markdown
<!-- [流程图] 描述：三层 CLAUDE.md 加载顺序... -->
![CLAUDE.md 层级示意图](../../../../assets/lessons-claudecode/cc005-claudemd-hierarchy.svg)
```

原因：注释是描述真相源。图片丢失或需重新生成时，注释里有完整描述。

**3. SVG 文件命名与存放**

- 命名：`<课程编号小写>-<slug>.svg`，如 `cc005-claudemd-hierarchy.svg`
- 存放：`assets/lessons-claudecode/`（或当前课程对应的 assets 目录）
- slug 从注释描述中提炼，2-4 个英文词，用 `-` 连接

**4. SVG 质量要求**

- **字体**：`'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif`
- **画布**：`viewBox="0 0 620 480"`，width/height 均写明
- **背景**：`#FAFAFA`，圆角 `rx="12"`
- **节点**：浅色背景 + 深色左侧色条（区块感），避免纯白底
- **文字大小**：标题 14-15px，正文 12-13px，说明 11px
- **箭头**：每条连线必须有文字标注（如「叠加」「触发」「返回」）
- **验证**：用 `open` 命令本地预览，确认渲染正常后再插入正文

---

### 更新：`course-generator/references/chapter-blueprint.md`

「视觉元素指南」部分的改动：

- 删除「截图/流程图/录屏无法由 AI 生成」的旧说法
- 改为：「`[流程图]` 和 `[对比图]` 由 AI 自动生成 SVG；`[截图]`/`[录屏建议]` 用占位标记供手动补充。详见 [image-protocol.md](image-protocol.md)」
- 占位标记格式本身保持不变

---

### 更新：`course-generator/SKILL.md`

在第 2 步（写正文）之后、第 3 步（质量门禁）之前，插入：

```
### Step 3.5：生成可自动化的视觉元素（SVG）

写完正文后，扫描本章所有 <!-- [流程图] --> 和 <!-- [对比图] --> 占位：

1. 读取 image-protocol.md，按质量要求为每个占位生成 SVG 文件
2. 用 `open` 命令本地预览确认渲染正常
3. 按 A方案约定，在注释下方紧接插入图片引用（保留注释不删）
4. [截图] 和 [录屏建议] 原样保留，不处理

注：每章通常 1-2 张，不会显著影响写章节的节奏。
若描述不够清晰导致 SVG 难以准确表达，报告用户并跳过该张（保留占位）。
```

---

### 更新：`course-campaign/SKILL.md`

在主循环的 Step D（进度报告）之后，全部章节完成时执行：

```
### Step E：图片完成度审计（全部章节 done 后执行一次）

用 grep 扫描本次 campaign 涉及的所有章节文件：
- 统计已生成 SVG 数（图片引用行数）
- 统计仍为占位的 [截图] 处数
- 统计 [录屏建议] 处数

输出格式：

  📊 图片完成度报告
  ✅ SVG 已生成：N 张
  📷 截图待补：N 处
     - CC-007:37 — Plan Mode 界面截图
     - ...
  🎬 录屏待录：N 处

此清单即录课行动清单，帮用户知道哪些需要手动补充。
```

---

## 数据流

```
course-generator 写正文
  → Step 3.5 扫描 [流程图]/[对比图]
    → 生成 SVG → assets/lessons-claudecode/
    → A方案插入（注释保留 + 图片引用追加）
  → [截图]/[录屏建议] 原样保留

course-campaign 全部章节完成
  → Step E grep 扫描所有章节文件
    → 输出图片完成度报告
```

---

## 不在本次范围内

- `[截图]` 的 mock/伪造截图生成（留待后续需要时扩展）
- campaign 进度文件里追踪图片状态字段（过度设计，重跑生成成本低）
- ZenMux/Imagen 生成封面或总结页（与此协议独立，另行使用 hd-infoimage skill）

---

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `course-generator/references/image-protocol.md` | 新建 |
| `course-generator/references/chapter-blueprint.md` | 更新「视觉元素指南」节 |
| `course-generator/SKILL.md` | 新增 Step 3.5 |
| `course-campaign/SKILL.md` | 新增 Step E |
