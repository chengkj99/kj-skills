# 知识地图设计系统

本文档说明 `assets/template.html` 的视觉系统与扩展方式。除非要新增配色或调整版式，一般无需阅读。

## 视觉令牌（CSS 变量）

定义在 `:root` 与 `body[data-theme=...]`：

| 变量 | 含义 |
|------|------|
| `--c1` ~ `--c6` | 6 个列/分组的强调色，按顺序循环（蓝/绿/紫/橙/金/青） |
| `--bg-1` / `--bg-2` | 背景渐变的两端色 |
| `--card-bg` / `--card-border` | 卡片背景与边框 |
| `--panel-bg` | 工作流面板背景 |
| `--text-1/2/3` | 文字三级层级：主/次/弱 |

强调色不在主题里切换——它跨主题保持鲜亮，只有背景和文字随主题变。

## 三套内置主题

`DATA.theme` 可选：

- `dark`（默认）：深蓝黑底，对标参考图的科技感。
- `midnight`：稍亮的午夜蓝，对比更柔和。
- `ink`：近黑墨色，适合更克制的质感。

## 区块结构（从上到下）

1. **km-header** — 主标题（渐变文字）+ 副标题。
2. **km-flow** — 横向阶段流程条，step 间用 `›` 箭头分隔。建议 5-6 个，过多会挤。
3. **km-grid** — 主网格。列数由 `columns.length` 决定，CSS 用 `repeat(N,1fr)` 自适应。每列：顶部 3px 强调色条 + 居中标题 + 条目列表（编号 badge + 名称 + 小字）。
4. **km-tags** — 增强标签区，药丸卡片自动换行（`flex-wrap`），左侧 3px 强调色条。
5. **km-workflows** — 实战工作流面板，整框用强调色描边。含标题 + 流程串 + 编号步骤。
6. **km-advice** — 底部 3 列建议框，emoji 图标 + 标题 + `▸` 要点列表。
7. **km-footer** — 页脚金句 banner。

## 排版经验法则

- **列数 4-6 最佳**。低于 4 显单薄，高于 6 在 1200px 画布下会拥挤。
- **每列条目 3-5 条**，且各列数量尽量均衡，视觉才整齐。
- **条目名简短**（关键词/工具名/概念），**说明 4-12 字**白话注解。
- 画布固定 `#map { width: 1200px }`，便于稳定截图。若内容特别多需要更宽，可调此值。

## 扩展：新增配色主题

在 `<style>` 里仿照现有主题加一段：

```css
body[data-theme="forest"] {
  --bg-1: #0a160f; --bg-2: #102218;
  --card-bg: rgba(255,255,255,0.03); --card-border: rgba(255,255,255,0.08);
  --text-1: #eaf5ee; --text-2: #93b3a0; --text-3: #5f7d6c;
  --panel-bg: rgba(255,255,255,0.02);
}
```

然后设 `DATA.theme = "forest"`。如需换强调色调色板，改 `:root` 的 `--c1`~`--c6` 即可，全图同步生效。

## 导出为图片

模板是纯 HTML，浏览器整页截图即得长图。也可用无头浏览器批量导出，例如：

```bash
# 需本机有 chrome / chromium
chrome --headless --screenshot=map.png --window-size=1280,2400 --hide-scrollbars knowledge-map-xxx.html
```

实际高度按内容调整 `--window-size` 的第二个值，或用 `--screenshot` 配合全页截图工具（如 puppeteer/playwright 的 `fullPage: true`）。
