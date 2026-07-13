# docx 生成技术规范

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
const OUTPUT_DIR = resolveOutputDir();
const TOPIC = "工具名称";   // 替换为实际主题名

function resolveOutputDir() {
  if (process.env.TUTORIAL_GUIDE_OUTPUT_DIR) {
    return process.env.TUTORIAL_GUIDE_OUTPUT_DIR;
  }

  let dir = process.cwd();
  while (dir !== path.dirname(dir)) {
    if (path.basename(dir) === 'kj-llm-wiki') {
      return path.join(dir, 'raw', 'papers');
    }
    dir = path.dirname(dir);
  }

  throw new Error('未找到 kj-llm-wiki 仓库根目录。请在 kj-llm-wiki 内运行脚本，或设置 TUTORIAL_GUIDE_OUTPUT_DIR。');
}

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
// 两个文件写入同一目录：默认是当前工作目录所属 kj-llm-wiki 仓库的 raw/papers/
const OUTPUT_DIR = resolveOutputDir();
// docx: OUTPUT_DIR/[主题名]-完全新手指南.docx
// md:   OUTPUT_DIR/[主题名]-完全新手指南.md
```

### 验证
```bash
# 确认两个文件都已生成
ls -lh "$(pwd)/raw/papers/" | grep "完全新手指南"
```
