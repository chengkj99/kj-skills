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
- **画布**：`viewBox="0 0 620 480"` `width="620"` `height="480"`
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
