---
name: tutorial-guide
description: 生成完整专业的新手教程指南Word文档（.docx），带封面、目录、公众号/视频号引流图。当用户提供主题名称和可选链接，要求生成教程、指南、新手教程、完全新手指南时，必须使用此技能。触发词包括：教程、指南、新手教程、完全新手指南、手把手教程、入门教程，以及类似"给我一份XX指南"或"生成XX教程"的请求。
---

# 教程指南生成技能

为用户生成风格统一、内容完整、专业精美的新手教程指南，输出为 `.docx` Word 文档。

## 触发条件

用户提供：
- **主题名称**（必填）：如"微信小程序开发"、"Superpowers 完全新手教程"
- **参考链接**（可选）：官方文档、视频、文章等
- **二维码图片**（已内置）：公众号/视频号二维码存于 `assets/` 目录，无需用户提供

---

## 输出规范

- 格式：`.docx` Word 文档 + `.md` Markdown 文档（同时生成）
- 文件名：`[主题名]-完全新手指南.docx` / `[主题名]-完全新手指南.md`
- 保存路径：`/Users/didi/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki/raw/papers/`
- 使用 `docx` npm 包生成，脚本保存到 `skills/tutorial-guide/scripts/gen_[主题名].js`
- 脚本中同时生成 `.docx` 和 `.md` 两个文件到同一目录

---

## 文档结构（顺序固定）

### 1. 封面页
- 主标题：`[主题名称] 完全新手指南`（居中，36pt，粗体，深蓝色 `#1a73e8`）
- 副标题：`从零开始，手把手带你入门`（居中，18pt，灰色 `#5f6368`）
- 作者：`作者：[公众号名]`（居中，14pt）
- 日期：当前日期（居中，12pt，灰色）
- 封面后插入分页符

### 2. 目录页
- 标题"目录"（居中，Heading1 样式，深蓝色）
- **手动构建目录条目**（禁止使用 `TableOfContents` 组件——该组件需在 Word 中手动更新域才能显示，直接打开时目录为空）
- 目录条目格式：`前言`、`第一章 XXX`、`第二章 XXX` … 每行一个条目，使用普通段落（Normal 样式），字体 13pt，左对齐，行间距适中
- 目录后插入分页符

**手动目录段落示例：**
```javascript
// 目录条目示例（根据实际章节列表逐条生成）
new Paragraph({
  children: [
    new TextRun({ text: "前言", size: 26, font: "Arial" }),
    new TextRun({ text: "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t3", size: 26, font: "Arial", color: "888888" })
  ],
  spacing: { before: 80, after: 80 }
}),
new Paragraph({
  children: [
    new TextRun({ text: "第一章  概念介绍与核心原理", size: 26, font: "Arial" })
  ],
  spacing: { before: 80, after: 80 }
}),
// ... 以下按实际章节逐条手动列出
```

> ⚠️ 注意：页码可写固定占位（如省略或标注"—"），但章节名称**必须与正文标题完全一致**，目录条目必须完整列出所有章节和小节标题。

### 3. 前言
- Heading1："前言"
- 正文介绍：这个工具/技术是什么、能解决什么问题、适合哪些读者

### 4. 正文章节（5-15 章，根据主题内容量合理设计）

章节数量规则：
- 简单工具/入门主题：5-8 章
- 中等复杂度开发框架：8-12 章
- 综合性平台/语言：10-15 章

每章必须包含：
- `Heading1`：`第X章 [章节名]`
- `Heading2`：各小节（每章至少 2-3 个小节）
- **锚点开场**：用具体场景/问题/反常识提问引入，禁止"本章介绍……"
- 正文段落：说人话、短句优先，步骤具体可操作，不水字数
- **真实踩坑**：至少 1 个真实易错点，写出具体报错信息或误区表现
- 有序/无序列表（使用 numbering config，禁止手动插入 bullet 符号）
- 代码块（Courier New 等宽字体 + 浅灰背景段落，代码必须可直接运行）
- 提示框（带边框底色段落，前缀：💡小贴士 / ⚠️注意 / ✅最佳实践）

典型章节参考（根据主题灵活调整）：
- 第一章：概念介绍与核心原理
- 第二章：环境准备与安装配置
- 第三章：快速入门（Hello World）
- 第四章：核心功能详解
- 第五章：常用 API / 组件
- 第六章：数据管理与状态
- 第七章：界面设计与样式
- 第八章：调试与测试
- 第九章：发布与部署
- 第十章：实战案例
- 第十一章：进阶技巧
- 第十二章：常见问题与排错
- 末章：总结与学习路线

### 5. 公众号 & 视频号引流页（固定，每次必须包含）

放在文档末尾，分页符后另起一页：

**标题**：`关注我，获取更多教程`（居中，Heading1，蓝色）

**引导语**（居中段落）：
> 感谢阅读这份指南！如果对你有帮助，欢迎关注我的公众号和视频号，获取更多实用技术教程、工具测评和行业干货 🎉

**二维码区域：使用 2 列无边框 Table，两个二维码并排同行展示**

每列单元格从上到下：
1. 平台标题（`📱 公众号` 或 `📹 视频号`，居中粗体）
2. 二维码图片（`ImageRun`，1.5英寸×1.5英寸 = 1371600 EMU）或占位说明文字
3. 说明文字（居中，如"扫码关注，获取图文教程"）

Table 规范：
- 表格宽度：`9360 DXA`，两列各 `4680 DXA`
- 所有边框设为 `BorderStyle.NONE`（无边框）
- 单元格内容水平居中、垂直居中
- 二维码图片**已内置**，直接读取以下路径，无需用户提供：
  - 公众号二维码：`<skill目录>/assets/qr-gongzhonghao.jpg`
  - 视频号二维码：`<skill目录>/assets/qr-shipinhao.jpg`
- 运行时用 `fs.readFileSync(path)` 读取图片 buffer，传入 `ImageRun`

**二维码嵌入示例：**
```javascript
const path = require('path');
// 脚本在 skills/tutorial-guide/scripts/ 下，assets 在上一级
const ASSETS = path.resolve(__dirname, '../assets');
const qrGzh = fs.readFileSync(path.join(ASSETS, 'qr-gongzhonghao.jpg'));
const qrSyh = fs.readFileSync(path.join(ASSETS, 'qr-shipinhao.jpg'));

new ImageRun({
  data: qrGzh,
  transformation: { width: 144, height: 144 }, // 约 1.5 英寸
  type: 'jpg',
  altText: { title: '公众号二维码', description: '程序员AI破局指南', name: 'qr-gzh' }
})
```

**结尾**（居中段落）：
> 💬 有问题？欢迎在公众号后台留言，我会及时回复！

---

## docx 生成技术规范

### 依赖安装
```bash
npm install -g docx
```

### 标准 imports
```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, HeadingLevel, AlignmentType, LevelFormat, BorderStyle,
        WidthType, ShadingType, VerticalAlign, PageBreak, Footer, PageNumber,
        PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader } = require('docx');
const fs = require('fs');
const path = require('path');
// 禁止引入 TableOfContents，目录必须手动构建
```

### 主题配色系统（Theme System）

**生成前必做**：根据工具/框架的官方品牌色选择或自定义主题，使封面、表头、note 框颜色与工具视觉一致。

```javascript
// ── 内置主题预设 ───────────────────────────────────────────────
const TOOL_THEMES = {
  // 默认深蓝主题（无明确品牌色时使用）
  default: {
    primary:  "1A3A6B", accent:   "2E75B6", accent2:  "C45911",
    lightBg:  "EBF3FB", headerBg: "1A3A6B",
    coverBg:  "1A3A6B", coverSub: "A8CCEB", strip: "C45911",
    mutedText:"666666", white:    "FFFFFF", black: "1A1A1A",
  },
  // Claude / Claude Code / Anthropic — 琥珀橙系
  claude: {
    primary:  "7C2D12", accent:   "C2410C", accent2:  "1E3A5F",
    lightBg:  "FFF7ED", headerBg: "7C2D12",
    coverBg:  "7C2D12", coverSub: "FDBA74", strip: "C2410C",
    mutedText:"78350F", white:    "FFFFFF", black: "1C1917",
  },
  // VS Code / GitHub Copilot — 深蓝紫系
  vscode: {
    primary:  "0D3B6E", accent:   "007ACC", accent2:  "6A0DAD",
    lightBg:  "E8F4FD", headerBg: "0D3B6E",
    coverBg:  "0D3B6E", coverSub: "87CEEB", strip: "007ACC",
    mutedText:"334155", white:    "FFFFFF", black: "0F172A",
  },
  // React / Next.js — 青蓝系
  react: {
    primary:  "0D4A6E", accent:   "0891B2", accent2:  "06B6D4",
    lightBg:  "E0F7FA", headerBg: "0D4A6E",
    coverBg:  "0D4A6E", coverSub: "80DEEA", strip: "0891B2",
    mutedText:"164E63", white:    "FFFFFF", black: "0C0A09",
  },
  // Vue / Nuxt — 祖母绿系
  vue: {
    primary:  "14532D", accent:   "059669", accent2:  "10B981",
    lightBg:  "ECFDF5", headerBg: "14532D",
    coverBg:  "14532D", coverSub: "6EE7B7", strip: "059669",
    mutedText:"166534", white:    "FFFFFF", black: "052E16",
  },
  // Python / Django / FastAPI — 蓝金系
  python: {
    primary:  "1A3A6B", accent:   "3776AB", accent2:  "F59E0B",
    lightBg:  "EBF3FB", headerBg: "1A3A6B",
    coverBg:  "1A3A6B", coverSub: "A8CCEB", strip: "3776AB",
    mutedText:"1E3A5F", white:    "FFFFFF", black: "1A1A1A",
  },
  // Docker / DevOps / Kubernetes — 深海蓝系
  docker: {
    primary:  "003F73", accent:   "2496ED", accent2:  "00D1B2",
    lightBg:  "E0F0FF", headerBg: "003F73",
    coverBg:  "003F73", coverSub: "93C5FD", strip: "2496ED",
    mutedText:"1E4976", white:    "FFFFFF", black: "0A1628",
  },
};

// ── 主题选择规则 ───────────────────────────────────────────────
// 工具名/主题名匹配（大小写不敏感）：
//   claude / claude code / anthropic / hermes      → claude
//   vscode / visual studio / copilot / github      → vscode
//   react / next.js / nextjs / remix               → react
//   vue / nuxt / vite（Vue 生态）                  → vue
//   python / django / fastapi / flask              → python
//   docker / kubernetes / k8s / devops             → docker
//   其他所有工具                                    → default

// ── 自定义主题（工具不在预设列表时）────────────────────────────
// 只需确定工具的主品牌色（HEX），按以下规则派生：
//   primary  = 品牌色加深 30%（用于标题、表头背景）
//   accent   = 品牌色原值（用于 H2、链接、边框）
//   accent2  = 互补色或对比色（橙系配蓝，蓝系配橙）
//   lightBg  = 品牌色透明度 8%（白底浅染，用于 note 背景）
//   coverSub = 品牌色浅化 50%（封面白底上的副标题）
//   strip    = 品牌色中等深度（封面数据条背景）

const C = TOOL_THEMES['claude']; // 替换为实际选择的主题 key
```

**常见工具品牌色速查：**

| 工具 / 框架 | 主品牌色 | 推荐主题 |
|------------|---------|---------|
| Claude Code / Anthropic | `#D97706` 琥珀橙 | `claude` |
| VS Code | `#007ACC` 蓝色 | `vscode` |
| GitHub / Copilot | `#0969DA` 蓝色 | `vscode` |
| React / Next.js | `#61DAFB` 青色 | `react` |
| Vue / Nuxt | `#42B883` 绿色 | `vue` |
| Python | `#3776AB` 蓝色 + `#FFD43B` 黄 | `python` |
| Docker | `#2496ED` 蓝色 | `docker` |
| TypeScript | `#3178C6` 蓝色 | `vscode` |
| Node.js | `#339933` 绿色 | `vue`（绿系） |
| Tailwind CSS | `#06B6D4` 青色 | `react`（青系） |

### 样式定义（使用主题变量 C）
```javascript
styles: {
  default: { document: { run: { font: "Arial", size: 24 } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 36, bold: true, color: C.primary, font: "Arial" },
      paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 28, bold: true, color: C.accent, font: "Arial" },
      paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 24, bold: true, color: C.primary, font: "Arial" },
      paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } }
  ]
}
```

### 页面设置（US Letter，1英寸边距）
```javascript
properties: {
  page: {
    size: { width: 12240, height: 15840 },
    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
  }
}
```

### 列表配置（必须使用，禁止手动 bullet）
```javascript
numbering: {
  config: [
    { reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
  ]
}
```

### 代码块样式
```javascript
// 深色代码块（推荐）
function code(lines) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
    rows: lines.map((line, i) => new TableRow({ children: [new TableCell({
      width: { size: 9360, type: WidthType.DXA },
      shading: { fill: "1E2A3A", type: ShadingType.CLEAR },
      margins: { top: 55, bottom: 55, left: 180, right: 180 },
      borders: {
        top:    { style: i === 0              ? BorderStyle.SINGLE : BorderStyle.NONE, size: 1, color: "3A5070" },
        bottom: { style: i === lines.length-1 ? BorderStyle.SINGLE : BorderStyle.NONE, size: 1, color: "3A5070" },
        left:   { style: BorderStyle.SINGLE, size: 6, color: C.accent2 },  // 左侧用 accent2 竖条
        right:  { style: BorderStyle.SINGLE, size: 1, color: "3A5070" },
      },
      children: [new Paragraph({
        children: [new TextRun({ text: line || " ", font: "Courier New", size: 18, color: "A8FF60" })],
        spacing: { after: 0 },
      })],
    })]})
    ),
  });
}
```

### 提示框样式（使用主题色 + 语义色）
```javascript
// note 框根据前缀 emoji 自动选配色（始终使用语义色，与主题无关）
// 💡 小贴士 / 📌 注意事项 — 使用主题 lightBg + accent 边框
{ shading: { fill: C.lightBg,  type: ShadingType.CLEAR },
  border:  { left: { style: BorderStyle.SINGLE, size: 16, color: C.accent } } }

// ⚠️ 警告 — 黄色（固定，语义色不随主题变化）
{ shading: { fill: "FEF9E7", type: ShadingType.CLEAR },
  border:  { left: { style: BorderStyle.SINGLE, size: 16, color: "FBBC04" } } }

// ✅ 最佳实践 — 绿色（固定）
{ shading: { fill: "E6F4EA", type: ShadingType.CLEAR },
  border:  { left: { style: BorderStyle.SINGLE, size: 16, color: "34A853" } } }
```

### 分页符
```javascript
new Paragraph({ children: [new PageBreak()] })
```

### 引流页 Table（2列并排，关键代码）
```javascript
new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4680, 4680],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders: {
            top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
            left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }
          },
          width: { size: 4680, type: WidthType.DXA },
          verticalAlign: VerticalAlign.CENTER,
          margins: { top: 200, bottom: 200, left: 200, right: 200 },
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "📱 公众号", bold: true, size: 24 })] }),
            // ImageRun 或占位段落
            new Paragraph({ alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "扫码关注，获取图文教程", size: 20, color: "5f6368" })] })
          ]
        }),
        // 第二列：视频号（同结构）
      ]
    })
  ]
})
```

### Markdown 同步生成

在同一个 Node.js 脚本末尾，生成 `.md` 文件到相同目录：

```javascript
// ── 同步生成 Markdown ────────────────────────────────────────────
const OUTPUT_DIR = "/Users/didi/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki/raw/papers";
const TOPIC = "工具名称";   // 替换为实际主题名

// 1. 生成 docx
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(`${OUTPUT_DIR}/${TOPIC}-完全新手指南.docx`, buf);
  console.log(`✅ DOCX: ${TOPIC}-完全新手指南.docx`);

  // 2. 同时写入 Markdown（内容结构与 docx 一致，纯文本格式）
  fs.writeFileSync(`${OUTPUT_DIR}/${TOPIC}-完全新手指南.md`, generateMarkdown());
  console.log(`✅ MD:   ${TOPIC}-完全新手指南.md`);
});

// generateMarkdown() 返回字符串，与 docx 章节一一对应
function generateMarkdown() {
  return [
    `# ${TOPIC} 完全新手指南`,
    ``,
    `> 程序员康健 出品 · 公众号：程序员AI破局指南`,
    ``,
    `---`,
    ``,
    `## 目录`,
    ``,
    // 目录列表（与 docx 完全一致）
    `- [第一章  认识 ${TOPIC}](#第一章)`,
    `- [第二章  安装与环境准备](#第二章)`,
    // ... 逐章列出
    ``,
    `---`,
    ``,
    // 正文章节（每章用 ## 对应 H1，### 对应 H2）
    `## 第一章  认识 ${TOPIC}`,
    ``,
    `### 1.1  什么是 ${TOPIC}`,
    ``,
    `正文内容...`,
    ``,
    `> 💡 **提示**：note 框内容转为 blockquote`,
    ``,
    "```bash",
    `# 代码块保持原样`,
    "```",
    ``,
    // ... 后续章节
  ].join('\n');
}
```

**Markdown 格式规范：**

| docx 元素 | Markdown 对应 |
|----------|--------------|
| H1 章标题 | `## 第X章  标题` |
| H2 节标题 | `### X.X  标题` |
| H3 小节  | `#### X.X.X  标题` |
| note 提示框 | `> 💡 **提示**：内容` |
| 代码块    | ` ```语言\n代码\n``` ` |
| 有序列表  | `1. 条目` |
| 无序列表  | `- 条目` |
| 表格     | 标准 GFM 表格 `\| 列 \| 列 \|` |
| 页面分隔  | `---` |
| 封面信息  | frontmatter `---\ntitle:\nauthor:\ndate:\n---` |

### 输出路径确认
```javascript
// 两个文件写入同一目录
const OUTPUT_DIR = "/Users/didi/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki/raw/papers";
// docx: OUTPUT_DIR/[主题名]-完全新手指南.docx
// md:   OUTPUT_DIR/[主题名]-完全新手指南.md
```

### 验证
```bash
# 确认两个文件都已生成
ls -lh "/Users/didi/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki/raw/papers/" | grep "完全新手指南"
```

---

## 内容风格规范

教程正文**必须**遵循以下风格，这不是可选项——风格写错比内容写少更难弥补。

### 写作人设：同行，不是老师

用「我」叙事，以「已经踩过这个坑的同行」身份写，不是站讲台的讲师。  
把每一章的开场想成：**「一个用过这个工具的人，和朋友解释为什么值得学、怎么快速上手」**。

❌ 错误示范（AI 腔/教材腔）：
> 本章将系统介绍 XXX 的核心概念与使用方法，帮助读者建立完整的知识体系。

✅ 正确示范（康健风格）：
> 我第一次用 XXX 的时候，卡了两个小时在配置上——后来发现其实只需要改一个参数。这章就从这里开始。

---

### 五条硬规则

1. **开场要有锚点**：每章用一个具体场景/报错/反常识问题开头，禁止用"本章介绍……"
2. **说人话**：能用"改这个配置"就不说"修改对应配置项参数"；长句拆短句，读出来不绕口
3. **理性落地**：感性描述之后必须跟可操作步骤，"原来如此"之后必须跟"那么怎么做"
4. **暴露真实的坑**：每章至少 1 个"我当时就在这里踩坑了"，写出真实的报错信息或误区，不要编造完美的学习路径
5. **去 AI 味**：删掉以下句式——"值得注意的是"、"不难发现"、"总而言之"、"不仅如此"、"综上所述"、"这使得……成为可能"

---

### 禁止清单

- ❌ 段落开头大量用转折词堆砌（"然而"、"此外"、"因此"……连续出现）
- ❌ 每段结尾都总结一遍刚说过的话
- ❌ 用抽象词描述抽象概念（"高效"、"强大"、"灵活"……没有具体场景支撑）
- ❌ 把官方文档原文翻译一遍当内容
- ❌ 爹味口吻："你必须"、"正确做法是"、"切记"——改成"我的习惯是"、"推荐这样做"

---

## 内容深度标准

每章正文必须满足以下深度门槛，**不达标时必须通过 webSearch 调研补充**：

| 维度 | 达标标准 |
|------|----------|
| 概念解释 | 不止"是什么"，要说清"为什么这样设计"、"与同类方案的区别" |
| 操作步骤 | 每个关键步骤有完整命令/代码示例，说明预期输出或效果 |
| 常见坑 | 每章至少 1 个真实易错点，给出具体报错信息和解决方法 |
| 最佳实践 | 至少 1 条来自官方文档或社区共识的推荐做法，注明出处 |
| 深度指标 | 读者看完能独立完成该章节任务，而非只是了解概念 |

**深度自评**：写完每章后，问自己"一个完全不懂的新手能否按本章内容独立操作？"——如果不能，说明内容不够深，执行 webSearch 补充。

---

## 生成流程

1. **分析主题**：根据主题名和可选链接，推断技术领域、目标读者、内容复杂度
2. **选择主题配色**：根据工具品牌色从 `TOOL_THEMES` 中选择对应 key（或自定义），确定 `const C = TOOL_THEMES['xxx']`
3. **规划章节**：根据复杂度决定章节数（5-15章），设计适合该主题的结构，**提前列出完整章节大纲**
4. **调研补充（必要时）**：对知识储备不足或需要最新信息的章节，用 webSearch 调研后再写：
   - 搜索词示例：`"[主题] 入门教程 最佳实践"`、`"[主题] 常见错误 解决方案"`、`"[主题] 官方文档 快速开始"`
   - 优先参考：官方文档、GitHub README、知名技术博客（掘金/SegmentFault/MDN/dev.to）
   - 每章至少能提供 1 个具体的可运行示例或真实截图描述
5. **读取内置二维码**：公众号和视频号二维码已内置于 `skills/tutorial-guide/assets/`，直接读取 `qr-gongzhonghao.jpg` 和 `qr-shipinhao.jpg`，用 `fs.readFileSync` + `ImageRun` 嵌入，**禁止**用占位框替代
6. **编写 JS 脚本**：将完整文档内容写入 `skills/tutorial-guide/scripts/gen_[主题名].js`；脚本同时生成 `.docx` 和 `.md` 到 `kj-llm-wiki/raw/papers/`；目录页**按第 3 步大纲手动逐条**构建段落，不得使用 `TableOfContents`
7. **执行生成**：`node /Users/didi/ai_space/kj-skills/skills/tutorial-guide/scripts/gen_[主题名].js`
8. **自检（必做，不可跳过）**：对照下方质量检查清单逐项核查，如发现任意一项不达标，**修改脚本后重新执行**，直到全部通过
9. **验证文件**：`ls -lh "/Users/didi/Library/Mobile Documents/iCloud~md~obsidian/Documents/kj-llm-wiki/raw/papers/" | grep 完全新手指南` 确认两个文件都存在
10. **告知用户**：输出两个文件的完整路径，说明 `.docx` 可在 Word 打开，`.md` 已同步至 kj-llm-wiki

---

## 质量检查清单

**正确性优先，美化其次。以下前三项不达标禁止交付。**

- [ ] **主题配色**：已从 `TOOL_THEMES` 选择匹配工具品牌色的主题，封面/表头/note 颜色与工具视觉一致
- [ ] 封面：主标题、副标题、作者、日期齐全，封面后有分页符
- [ ] 目录：**手动构建**，条目与正文标题逐字一致，覆盖所有章节，目录后有分页符（**禁止使用 TableOfContents 组件**）
- [ ] 目录条目数量与正文章节数匹配，不遗漏任何 Heading1 / Heading2
- [ ] 章节数：5-15 章，根据主题内容量合理安排
- [ ] 每章至少 2 个 Heading2 小节，内容详细可操作
- [ ] 每章包含可运行代码/命令示例，至少 1 个常见坑 + 解决方法
- [ ] 内容不足时已通过 webSearch 调研补充，不靠泛泛描述凑字数
- [ ] 风格自查：无"本章介绍……"开场，无"值得注意的是/不难发现/综上所述"等 AI 腔套话
- [ ] 每章有具体场景锚点开场，有"同行视角"而非"讲师视角"
- [ ] 无爹味口吻（"你必须""切记""正确做法是"），改用"我的习惯是""推荐这样做"
- [ ] 列表使用 numbering config，未手动插入 bullet 符号
- [ ] 代码块使用 Courier New 等宽字体 + 深色背景（`1E2A3A`）+ 绿色代码字
- [ ] 提示框至少出现 3 次（💡小贴士 / ⚠️注意 / ✅最佳实践）
- [ ] 引流尾页：独立成页，公众号和视频号二维码并排一行（2列无边框 Table），有引导文案
- [ ] 二维码已从 `assets/qr-gongzhonghao.jpg` 和 `assets/qr-shipinhao.jpg` 读取并用 `ImageRun` 嵌入，**不得**用占位框替代
- [ ] **DOCX 文件**已写入 `kj-llm-wiki/raw/papers/[主题名]-完全新手指南.docx`
- [ ] **Markdown 文件**已同步生成到 `kj-llm-wiki/raw/papers/[主题名]-完全新手指南.md`，章节结构与 docx 一致
- [ ] 用 `ls` 命令确认两个文件都存在且大小非零

---

## 用户输入格式

```
给我一份 [主题名] 完全新手指南
生成一份 [主题名](链接) 教程
帮我写一个 [主题名] 的新手教程，链接：[URL]
```

技能自动补全所有缺失信息，无需向用户询问细节。

---

## 完成后提示

文档生成并验证通过后，在告知用户文件路径的同时，**主动提示**：

> 📦 文档已生成完毕！如需为这篇教程准备公众号配套物料（前言、标题、摘要、封面图提示词、转发文案），可以说「帮我生成配套物料」或直接触发 `wechat-companion` 技能。
