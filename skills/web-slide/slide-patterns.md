# slide-patterns · 幻灯片 HTML 模式库

AI 生成幻灯片时按此文件选取对应模式，**直接复制模板并填充内容**。所有 CSS 已在框架前段定义，不需要额外添加样式。

---

## 目录

| # | 类型 | 类名 / 关键词 | 使用场景 |
|---|------|-------------|---------|
| 1 | [封面（无图）](#1-封面无图版) | `slide cover` + 装饰右半区 | 无背景图时的封面，最常用 |
| 2 | [封面（有图）](#2-封面有图版) | `slide cover` + cover-hero-img | 有高质量背景图时 |
| 3 | [章节幕（标准）](#3-章节幕标准) | `slide chapter` | 章节之间的过渡 |
| 4 | [章节幕（路线图）](#4-章节幕路线图变体) | `ch-layout--roadmap` | 章节内含多步骤预览 |
| 5 | [章节幕（全景背景图）](#5-章节幕全景背景图变体) | CSS per-id override | 全屏图片章节页，视觉震撼 |
| 6 | [讲者介绍](#6-讲者介绍页) | s01b-* | 封面后讲者背景介绍 |
| 7 | [目录（TOC）](#7-目录页) | toc-grid + toc-item | 演讲开始时总览 |
| 8 | [级别进阶](#8-级别进阶页) | s02b-panel | 受众级别/阶段递进 |
| 9 | [标准内容](#9-标准内容页) | `slide` + points | 最常用正文页 |
| 10 | [角色技能网格](#10-角色技能网格页) | role-skills-layout | 展示多角色工具矩阵 |
| 11 | [Mermaid 流程图](#11-mermaid-流程图页) | `slide-mermaid-lg` | 时序图/流程图 |
| 12 | [三列卡片](#12-三列卡片页) | cards-3col | 三个并列概念 |
| 13 | [时间轴卡片](#13-时间轴卡片页) | tl-item | 步骤/阶段/编号概念 |
| 14 | [双栏对比表格](#14-双栏对比表格页) | compare-table + s6-flow | 旧vs新、两列对比 |
| 15 | [图文分栏](#15-图文分栏页) | 图片列+文字列 | 图示说明某个概念 |
| 16 | [diff 对比框](#16-diff-对比框页) | diff-row + diff-box | ❌ 不适合 vs ✅ 适合 |
| 17 | [代码页](#17-代码页) | Prism.js | 展示代码片段 |
| 18 | [金句页](#18-金句页) | blockquote | 突出一句核心观点 |
| 19 | [Q&A 最终页](#19-qa-最终页) | qa-layout + qa-qr | 演讲结束页 |

---

## 1. 封面（无图版）

推荐默认使用。右半区用装饰几何元素平衡视觉重量。

```html
<!-- ===== 封面 ===== -->
<section
  class="slide cover active"
  id="s01"
  data-notes="口播内容写这里。介绍演讲主题和今天要解决什么问题。"
>
  <div class="cover-bg" aria-hidden="true"></div>
  <div class="cover-content">
    <div class="cover-kicker">副主题标签 · 系列名称</div>
    <div class="cover-title">
      主标题第一行<br /><span>高亮关键词</span>
    </div>
    <div class="cover-subtitle">
      一句话说明这场演讲要解决什么
    </div>
    <div class="cover-meta">
      <p><strong>讲者姓名</strong> · 身份标签 ｜ 团队/公司</p>
    </div>
  </div>
  <!-- 装饰右半区：无封面图时平衡视觉重量 -->
  <div aria-hidden="true" style="
    position:absolute;right:0;top:0;width:42%;height:100%;
    pointer-events:none;overflow:hidden;
  ">
    <div style="
      position:absolute;right:-80px;top:50%;transform:translateY(-50%);
      width:420px;height:420px;border-radius:50%;
      border:2px solid rgba(77,126,245,0.15);
    "></div>
    <div style="
      position:absolute;right:-20px;top:50%;transform:translateY(-50%);
      width:280px;height:280px;border-radius:50%;
      border:1px solid rgba(77,126,245,0.08);
    "></div>
    <div style="
      position:absolute;right:160px;top:50%;transform:translateY(-50%);
      width:2px;height:32%;
      background:linear-gradient(to bottom,transparent,rgba(77,126,245,0.6),transparent);
    "></div>
    <div style="
      position:absolute;right:2vw;bottom:6vh;
      display:flex;flex-direction:column;gap:8px;align-items:flex-end;
    ">
      <div style="width:100px;height:3px;background:rgba(77,126,245,0.5);border-radius:2px;"></div>
      <div style="width:60px;height:3px;background:rgba(255,255,255,0.15);border-radius:2px;"></div>
    </div>
  </div>
</section>
```

---

## 2. 封面（有图版）

提供高质量图片时使用。图片放 `cover-bg` 里，框架 CSS 自动加渐变遮罩。

```html
<section
  class="slide cover active"
  id="s01"
  data-notes="口播内容写这里。"
>
  <div class="cover-bg" aria-hidden="true">
    <img src="cover.png" alt="" class="cover-hero-img" width="1920" height="1080" />
  </div>
  <div class="cover-content">
    <div class="cover-kicker">副主题标签 · 系列名称</div>
    <div class="cover-title">
      主标题第一行<br /><span>高亮关键词</span>
    </div>
    <div class="cover-subtitle">一句话说明这场演讲要解决什么</div>
    <div class="cover-meta">
      <p><strong>讲者姓名</strong> · 身份标签 ｜ 团队/公司</p>
    </div>
  </div>
</section>
```

---

## 3. 章节幕（标准）

章节之间的过渡页，大字标题，大号数字装饰。Logo 自动切换为白色版本。

```html
<!-- ===== Chapter N ===== -->
<section
  class="slide chapter"
  id="s03"
  data-notes="这一章的核心问题是……"
>
  <div class="ch-layout">
    <div class="ch-main">
      <div class="ch-num">Part 01 · 章节名称篇</div>
      <div class="ch-title">这一章的核心论点，<span>关键词高亮</span></div>
      <div class="ch-sub">一句话补充说明或引导问题</div>
    </div>
    <div class="ch-aside" aria-hidden="true">
      <span class="ch-part-mark">01</span>
    </div>
  </div>
</section>
```

---

## 4. 章节幕（路线图变体）

章节开始时展示本章的 3 个子步骤。在标准章节幕基础上加 `ch-layout--roadmap` 和 `ch-roadmap`。

```html
<section
  class="slide chapter"
  id="s08"
  data-notes="本章分三步……"
>
  <div class="ch-layout ch-layout--roadmap">
    <div class="ch-main">
      <div class="ch-num">Part 02 · 方法篇</div>
      <div class="ch-title">如何把经验变成 <span>Skill</span></div>
    </div>
    <div class="ch-aside" aria-hidden="true">
      <span class="ch-part-mark">02</span>
    </div>
    <div class="ch-roadmap">
      <div class="ch-roadmap-item">
        <div class="ch-roadmap-num">STEP 01</div>
        <div class="ch-roadmap-title">第一步标题</div>
        <div class="ch-roadmap-desc">简短描述，15 字内</div>
      </div>
      <div class="ch-roadmap-sep" aria-hidden="true"></div>
      <div class="ch-roadmap-item">
        <div class="ch-roadmap-num">STEP 02</div>
        <div class="ch-roadmap-title">第二步标题</div>
        <div class="ch-roadmap-desc">简短描述</div>
      </div>
      <div class="ch-roadmap-sep" aria-hidden="true"></div>
      <div class="ch-roadmap-item">
        <div class="ch-roadmap-num">STEP 03</div>
        <div class="ch-roadmap-title">第三步标题</div>
        <div class="ch-roadmap-desc">简短描述</div>
      </div>
    </div>
  </div>
</section>
```

---

## 5. 章节幕（全景背景图变体）

使用页面级 CSS 覆盖为全屏图片背景。需在 `<style>` 段（框架前段末尾之后、slides 之前）添加一段 CSS。

> 注意：CSS 必须写在 `<style>` 标签内，加在框架 CSS 末尾 `</style>` 之前（行 4763 附近），或用 `<style>` 新块插在 slides 前。

```html
<!-- 全景背景图页需要在 PRE_CONTENT 里补充此 CSS（追加到 </style> 之前）-->
<!--
#s-panorama.slide.chapter {
  background:
    url('your-panorama.png') center right / cover no-repeat,
    var(--ink);
}
#s-panorama.slide.chapter::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to right,
    rgba(5, 12, 28, 0.82) 0%,
    rgba(5, 12, 28, 0.55) 50%,
    rgba(5, 12, 28, 0.15) 100%
  );
  pointer-events: none;
  z-index: 0;
}
-->
<section
  class="slide chapter"
  id="s-panorama"
  data-notes="升华收束口播……"
>
  <div class="ch-layout">
    <div class="ch-main">
      <div class="ch-num is-screen-hidden" aria-hidden="true">结语</div>
      <div class="ch-title">
        AI 不会替代你<br />它是你<span>能力的延伸</span>
      </div>
      <div class="ch-sub">
        望远镜 = 视力的延伸 &nbsp;·&nbsp; AI = 大脑的延伸
      </div>
    </div>
    <div class="ch-aside" aria-hidden="true">
      <span class="ch-part-mark is-epilogue">✦</span>
    </div>
  </div>
</section>
```

---

## 6. 讲者介绍页

封面后讲者背景介绍，左侧阶梯递进 + 右侧 blockquote。需在 PRE_CONTENT 末尾追加专属 CSS（`slide-patterns.md` 末尾附有所需 CSS）。

```html
<section
  class="slide"
  id="s01b"
  data-notes="自我介绍……"
>
  <div class="slide-label is-screen-hidden" aria-hidden="true">讲者介绍</div>
  <div class="slide-title">从「前端 Worker」到 <em>Builder</em></div>
  <div class="content">
    <div class="s01b-body">
      <div class="s01b-intro">
        <div class="s01b-name">程康健</div>
        <div class="s01b-role">信贷研发 · AI 编程实践</div>
        <p class="s01b-bio">
          过去习惯叫自己<em>「前端」</em>——
          工种标签容易框住人，也遮住了我们真正在交付什么。
        </p>
      </div>
      <div class="s01b-ladder">
        <div class="s01b-step s01b-step--1">
          <span class="s01b-step-num">01</span>
          <div class="s01b-step-main">
            <strong>前端 / 后端</strong>
            <span>工种名称 · 容易被角色框住</span>
          </div>
        </div>
        <div class="s01b-step s01b-step--2">
          <span class="s01b-step-num">02</span>
          <div class="s01b-step-main">
            <strong>研发 · Engineer</strong>
            <span>解决复杂问题 · 偏过程交付</span>
          </div>
        </div>
        <div class="s01b-step s01b-step--3">
          <span class="s01b-step-tag">今天</span>
          <span class="s01b-step-num">03</span>
          <div class="s01b-step-main">
            <strong>Builder</strong>
            <span>构造产品 · 直接拿结果</span>
          </div>
        </div>
      </div>
    </div>
    <div class="s01b-quote">
      <blockquote>
        「一句有分量的引用，表达你对这个职业的核心观点。」
      </blockquote>
    </div>
  </div>
</section>
```

---

## 7. 目录页

演讲开始时总览全部章节，适合 3–6 个章节。

```html
<section
  class="slide"
  id="s02"
  data-notes="今天分享几个部分……"
>
  <div class="slide-label">目录</div>
  <div class="slide-title">今天分享的五个部分</div>
  <div class="content">
    <div class="toc-grid">
      <div class="toc-item">
        <div class="toc-num">01</div>
        <div class="toc-content">
          <strong>章节标题</strong>
          <span>一句话说明本章内容</span>
        </div>
      </div>
      <div class="toc-item">
        <div class="toc-num">02</div>
        <div class="toc-content">
          <strong>章节标题</strong>
          <span>一句话说明本章内容</span>
        </div>
      </div>
      <div class="toc-item">
        <div class="toc-num">03</div>
        <div class="toc-content">
          <strong>章节标题</strong>
          <span>一句话说明本章内容</span>
        </div>
      </div>
    </div>
  </div>
</section>
```

---

## 8. 级别进阶页

展示受众分级或能力阶段，每行「当前状态 → 目标状态」。

```html
<section
  class="slide"
  id="s02b"
  data-notes="找到自己的一级，往上走一级……"
>
  <div class="slide-label">目标分级</div>
  <div class="slide-title">找到自己的一级，<em>往上走一级</em></div>
  <div class="slide-core">
    不论你现在处于哪个阶段，今天都有明确收获。
  </div>
  <div class="content">
    <div class="s02b-panel">
      <div class="s02b-step s02b-step--1">
        <span class="s02b-num">01</span>
        <div class="s02b-from">当前状态描述</div>
        <div class="s02b-arrow" aria-hidden="true">→</div>
        <div class="s02b-to">目标能力</div>
      </div>
      <div class="s02b-step s02b-step--2">
        <span class="s02b-num">02</span>
        <div class="s02b-from">当前状态描述</div>
        <div class="s02b-arrow" aria-hidden="true">→</div>
        <div class="s02b-to">目标能力</div>
      </div>
      <div class="s02b-step s02b-step--3">
        <span class="s02b-num">03</span>
        <div class="s02b-from">当前状态描述</div>
        <div class="s02b-arrow" aria-hidden="true">→</div>
        <div class="s02b-to">目标能力</div>
      </div>
      <!-- 全员高亮步骤（s02b-tag 标注） -->
      <div class="s02b-step s02b-step--5">
        <span class="s02b-tag">全员</span>
        <span class="s02b-num">04</span>
        <div class="s02b-from">全员适用的状态</div>
        <div class="s02b-arrow" aria-hidden="true">→</div>
        <div class="s02b-to">最终目标</div>
      </div>
    </div>
    <p class="s02b-footer">
      多级递进 · <em>走上一级就是胜利</em>
    </p>
  </div>
</section>
```

---

## 9. 标准内容页

最常用的页面类型。标题 + 核心句 + 要点列表。

```html
<section
  class="slide"
  id="s04"
  data-notes="口播：先说核心结论，再展开要点……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title">页面标题，<em>关键词高亮</em></div>
  <div class="slide-core">
    一句话核心结论，控制在 30 字以内。
  </div>
  <div class="content">
    <ul class="points">
      <li><strong>要点一</strong> — 简短说明，15 字内</li>
      <li><strong>要点二</strong> — 简短说明</li>
      <li><strong>要点三</strong> — 简短说明</li>
      <li><strong>要点四</strong> — 简短说明</li>
    </ul>
  </div>
</section>
```

**带底部说明行的变体**（在 content 后加）：

```html
  <p class="slide-footer">
    <span class="slide-footer-text">底部补充说明，或一句引导性问题</span>
  </p>
```

---

## 10. 角色技能网格页

展示多个角色/工种及其对应工具。适合「各行业的 AI 工具矩阵」类内容。

```html
<section
  class="slide"
  id="s10"
  data-notes="各职能都有对应的 Skill……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title">各工种 <em>Skill 工具矩阵</em></div>
  <div class="slide-core">
    高手经验已被 Skill 打包普及，执行经验正在被社区能力包替代。
  </div>
  <div class="content">
    <div class="role-skills-layout">
      <div class="role-tier-label">
        各工种典型 Skill · 执行经验正被社区能力包替代
      </div>
      <div class="role-skills-grid role-skills-grid--2x3">
        <div class="role-skill-card">
          <div class="role-name">开发</div>
          <ul class="role-skills">
            <li class="skill-row">
              <code>/requesting-code-review</code>
              <span class="skill-hint">代码评审</span>
            </li>
            <li class="skill-row">
              <code>/systematic-debugging</code>
              <span class="skill-hint">系统化排错</span>
            </li>
          </ul>
        </div>
        <div class="role-skill-card">
          <div class="role-name">产品</div>
          <ul class="role-skills">
            <li class="skill-row">
              <code>/brainstorming</code>
              <span class="skill-hint">需求脑暴</span>
            </li>
            <li class="skill-row">
              <code>/writing-plans</code>
              <span class="skill-hint">项目计划</span>
            </li>
          </ul>
        </div>
        <div class="role-skill-card role-skill-card--other">
          <div class="role-name">其他职能</div>
          <ul class="role-skills">
            <li class="skill-row">
              <code>/ai-coding-weekly-report</code>
              <span class="skill-hint">AI 编程中文周报</span>
            </li>
          </ul>
          <p class="role-more-coverage">还覆盖更多……</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

**网格变体：**
- `role-skills-grid--3` — 3 列
- `role-skills-grid--2x3` — 2×3 网格（最常用）
- `role-skills-grid--2` — 2 列大卡片
- `role-skills-grid--6` — 6 列紧凑

---

## 11. Mermaid 流程图页

翻到该页时自动渲染。`data-diagram` 必须全局唯一。

```html
<section
  class="slide slide-mermaid-lg"
  id="s15"
  data-notes="这个流程图展示了……从左到右依次是……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title"><em>交互流程图</em></div>
  <div class="slide-core">一句话说明流程的核心逻辑。</div>
  <div class="content">
    <div class="mermaid-wrap">
      <div class="mermaid-fit">
        <pre class="mermaid" data-diagram="unique-diagram-id">
sequenceDiagram
    actor 用户
    participant 系统A
    participant 系统B

    用户->>系统A: 发起请求
    系统A->>系统B: 转发处理
    系统B-->>系统A: 返回结果
    系统A-->>用户: 响应
        </pre>
      </div>
    </div>
  </div>
</section>
```

**常用 Mermaid 图类型：**
- `sequenceDiagram` — 时序图（系统交互）
- `flowchart LR` — 水平流程图
- `flowchart TD` — 垂直流程图
- `graph TD` — 依赖关系图

---

## 12. 三列卡片页

三个并列的概念/步骤。可以是普通 card 或 s18-card（带编号标题）或 s35-step-card（步骤卡）。

**普通 card 版：**

```html
<section
  class="slide"
  id="s12"
  data-notes="三个核心概念……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title"><em>三个</em>核心要素</div>
  <div class="slide-core">一句话说明三者关系。</div>
  <div class="content">
    <div class="cards-3col cards-3col--gap-6">
      <div class="card">
        <div class="card-title">概念一</div>
        <div class="card-body">说明文字，可以有 <code>code</code> 和 <strong>强调</strong>。</div>
      </div>
      <div class="card">
        <div class="card-title">概念二</div>
        <div class="card-body">说明文字。</div>
      </div>
      <div class="card">
        <div class="card-title">概念三</div>
        <div class="card-body">说明文字。</div>
      </div>
    </div>
  </div>
</section>
```

**s18-card 版（带序号 + 要点）：**

```html
    <div class="cards-3col cards-3col--gap-6">
      <div class="card s18-card">
        <div class="s18-card-head">
          <span class="s18-card-num">01</span>
          <div class="s18-card-title">卡片标题</div>
        </div>
        <ul class="points">
          <li><strong>要点</strong> — 说明</li>
        </ul>
      </div>
      <!-- 重复 3 次 -->
    </div>
```

**s35-step-card 版（步骤卡，含链接）：**

```html
    <div class="cards-3col cards-3col--gap-6">
      <div class="s35-step-card">
        <div class="s35-step-num">01</div>
        <div class="s35-step-title">步骤标题</div>
        <a class="s35-step-link" href="https://..." target="_blank" rel="noopener">链接文字</a>
        <ul class="points">
          <li><code>命令</code> — 说明</li>
          <li>要点说明</li>
        </ul>
      </div>
    </div>
```

---

## 13. 时间轴卡片页

带编号的步骤/阶段列表，用 `tl-item` 展现带年份/序号的时间轴。

```html
<section
  class="slide"
  id="s34"
  data-notes="三件事……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title"><em>三步</em>搞定 XXX</div>
  <div class="slide-core">一句话说明。</div>
  <div class="content">
    <div class="cards-3col cards-3col--gap-6">
      <div>
        <div class="tl-item">
          <div class="tl-year">01</div>
          <div class="tl-event">步骤名称</div>
          <div class="tl-detail">
            具体操作说明，可有 <code>代码</code>。<br />可以换行。
          </div>
        </div>
      </div>
      <div>
        <div class="tl-item">
          <div class="tl-year">02</div>
          <div class="tl-event">步骤名称</div>
          <div class="tl-detail">具体操作。</div>
        </div>
      </div>
      <div>
        <div class="tl-item">
          <div class="tl-year">03</div>
          <div class="tl-event">步骤名称</div>
          <div class="tl-detail">具体操作。</div>
        </div>
      </div>
    </div>
  </div>
</section>
```

---

## 14. 双栏对比表格页

左栏：对比表格（旧→新）；右栏：流程步骤。适合「能力迁移」「纵向升维+横向扩界」类内容。

```html
<section
  class="slide"
  id="s06"
  data-notes="纵向升维：岗位内从执行到判断……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title">驾驭 AI：<em>两层</em>能力迁移</div>
  <div class="slide-core">
    纵向：岗位内从「执行」升到「判断」；横向：突破岗位边界。
  </div>
  <div class="content s6-body">
    <div class="s6-col">
      <header class="s6-col-head">
        <span class="s6-col-icon" aria-hidden="true">↕</span>
        ① 纵向 · 岗位内升维
      </header>
      <table class="compare-table s6-table">
        <thead>
          <tr>
            <th>角色</th>
            <th>以前</th>
            <th>现在</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>角色A</strong></td>
            <td>旧行为</td>
            <td>新行为</td>
          </tr>
          <tr>
            <td><strong>角色B</strong></td>
            <td>旧行为</td>
            <td>新行为</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="s6-vrule" aria-hidden="true"></div>
    <div class="s6-col">
      <header class="s6-col-head">
        <span class="s6-col-icon" aria-hidden="true">↔</span>
        ② 横向 · 突破边界
      </header>
      <div class="s6-flow">
        <div class="s6-flow-step">
          <span class="s6-flow-num">01</span>
          <div class="s6-flow-title">发现</div>
          <div class="s6-flow-detail">用户痛点</div>
        </div>
        <span class="s6-flow-arrow" aria-hidden="true">→</span>
        <div class="s6-flow-step">
          <span class="s6-flow-num">02</span>
          <div class="s6-flow-title">定义</div>
          <div class="s6-flow-detail">边界与验收</div>
        </div>
        <span class="s6-flow-arrow" aria-hidden="true">→</span>
        <div class="s6-flow-step">
          <span class="s6-flow-num">03</span>
          <div class="s6-flow-title">交付</div>
          <div class="s6-flow-detail">AI 执行</div>
        </div>
      </div>
      <ul class="points s6-points">
        <li><strong>关键点</strong>：说明</li>
      </ul>
    </div>
  </div>
  <div class="s6-footer">
    底部总结句，<em>关键词高亮</em>
  </div>
</section>
```

---

## 15. 图文分栏页

左侧图片说明某个概念，右侧文字卡片。适合可视化「概念模型」。

```html
<section
  class="slide"
  id="s06b"
  data-notes="这张图说明……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title">标题，<em>关键词高亮</em></div>
  <div class="slide-core">一句话核心结论。</div>
  <div class="content s6b-body">
    <div class="s6b-split">
      <div class="s6b-img-col">
        <img
          src="diagram.png"
          alt="图片描述"
          class="s6b-img"
        />
      </div>
      <div class="s6b-text-col">
        <div class="s6b-panel">
          <div class="s6b-section-label">五锚点 · 说明栏目标题</div>
          <div class="s6b-core-grid">
            <div class="s6b-core-card">
              <strong>概念一</strong>
              <span>简短描述</span>
            </div>
            <div class="s6b-core-card">
              <strong>概念二</strong>
              <span>简短描述</span>
            </div>
            <div class="s6b-core-card">
              <strong>概念三</strong>
              <span>简短描述</span>
            </div>
          </div>
          <!-- 可选：标签行 -->
          <div class="s6b-outer-row">
            <span class="s6b-outer-label">扩展项</span>
            <span class="s6b-outer-tag">标签1</span>
            <span class="s6b-outer-tag">标签2</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="s6b-footer">底部总结</div>
</section>
```

---

## 16. diff 对比框页

❌ 不适合 vs ✅ 适合，或两个方案对比。

```html
<section
  class="slide"
  id="s09"
  data-notes="左边是不适合的，右边是适合的……"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title"><em>判断</em>：值不值得做</div>
  <div class="slide-core">一句话说明判断标准。</div>
  <div class="content">
    <div class="diff-row">
      <div class="diff-box bad">
        <div class="diff-label">❌ 不适合</div>
        <ul class="points">
          <li>条件一</li>
          <li>条件二</li>
        </ul>
      </div>
      <div class="diff-box good">
        <div class="diff-label">✅ 适合</div>
        <ul class="points">
          <li>条件一</li>
          <li>条件二</li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

**中性对比变体（两边都用 `diff-box good`）：**

```html
    <div class="diff-row">
      <div class="diff-box good">
        <div class="diff-label">概念A</div>
        说明文字……
      </div>
      <div class="diff-box good">
        <div class="diff-label">概念B</div>
        说明文字……
      </div>
    </div>
```

---

## 17. 代码页

展示代码片段，Prism.js 自动高亮。

```html
<section
  class="slide"
  id="s08"
  data-notes="这段代码展示了……重点看第 N 行"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="slide-title">代码示例：<em>功能名称</em></div>
  <div class="slide-core">一句话说明这段代码解决什么问题。</div>
  <div class="content">
    <pre><code class="language-yaml">
# 支持语言：yaml / bash / javascript / typescript / python / json / markdown
name: my-skill
description: "描述这个 skill 做什么"
    </code></pre>
  </div>
</section>
```

**支持的 language class：**
- `language-yaml` · `language-bash` · `language-javascript` · `language-typescript`
- `language-python` · `language-json` · `language-markdown`

---

## 18. 金句页

突出一句有力的引用或核心观点。

```html
<section
  class="slide"
  id="s06"
  data-notes="这句话是整场演讲的核心论断，停顿一下让听众吸收。"
>
  <div class="slide-label">PPT N · 所属章节</div>
  <div class="content" style="display:flex;align-items:center;justify-content:center;height:100%;">
    <blockquote class="slide-quote">
      <p>「引用内容写这里，一句话，有力量，让人记得住。」</p>
      <cite>— 来源 / 出处</cite>
    </blockquote>
  </div>
</section>
```

---

## 19. Q&A 最终页

演讲结束，大字 Q&A + 二维码联系方式。

```html
<section
  class="slide"
  id="s-qa"
  data-notes="感谢大家的聆听！欢迎扫码加微信，继续交流。"
>
  <div class="qa-layout">
    <div class="qa-big">Q<em>&amp;</em>A</div>
    <div class="qa-divider"></div>
    <div class="qa-bottom">
      <div class="qa-contact-card">
        <div class="qa-card-label">微信 · WeChat</div>
        <div class="qa-qr-frame">
          <img src="wechat-qr.png" alt="微信二维码" class="qa-qr-img" />
        </div>
        <div class="qa-contact-name">讲者姓名</div>
      </div>
      <div class="qa-tagline">
        感谢聆听，欢迎提问。<br />
        也可加我好友，继续交流——<br />
        任何主题。
      </div>
    </div>
  </div>
</section>
```

**无二维码版（纯文字感谢）：**

```html
<section
  class="slide cover"
  id="s99"
  data-notes="感谢大家，有问题欢迎提问。"
>
  <div class="cover-content">
    <div class="cover-kicker">感谢收看</div>
    <div class="cover-title">
      Q <span>&amp; A</span>
    </div>
    <div class="cover-subtitle">欢迎提问 · 互动交流</div>
    <div class="cover-meta">
      <p><strong>讲者姓名</strong> · 联系方式</p>
    </div>
  </div>
  <!-- 装饰右半区（同封面） -->
  <div aria-hidden="true" style="
    position:absolute;right:0;top:0;width:42%;height:100%;
    pointer-events:none;overflow:hidden;
  ">
    <div style="position:absolute;right:-80px;top:50%;transform:translateY(-50%);width:420px;height:420px;border-radius:50%;border:2px solid rgba(77,126,245,0.15);"></div>
    <div style="position:absolute;right:-20px;top:50%;transform:translateY(-50%);width:280px;height:280px;border-radius:50%;border:1px solid rgba(77,126,245,0.08);"></div>
    <div style="position:absolute;right:160px;top:50%;transform:translateY(-50%);width:2px;height:32%;background:linear-gradient(to bottom,transparent,rgba(77,126,245,0.6),transparent);"></div>
  </div>
</section>
```

---

## 通用规则

### id 命名
- 顺序递增：`s01` `s02` `s03` …
- 章节幕可用整数：`s03` `s10` `s20`
- 子页可加字母：`s01b` `s05a`
- Q&A 最终页用 `s-qa`

### data-notes 写法
- 口播内容放在 `data-notes="..."` 里
- 内容是自然语言，说给听众的话
- 引号用 `&quot;` 转义，或改用单引号包裹属性
- 长度：100–300 字

### em / span 高亮
- `<em>` 用于标题中的关键词（渲染为强调色）
- `<span>` 在 `.cover-title` 中用于高亮关键词
- 每页最多高亮 1–2 处

### 内容密度控制
- 要点：3–5 条
- 每条：≤ 20 字
- 核心句（slide-core）：≤ 30 字
- 章节幕：只有标题，无正文列表

### Logo 自动切换（无需手动操作）
框架 JS `updateBrandTheme()` 自动判断当前幻灯片类型：
- **深色 logo**（白色版本）：`cover`、`chapter`、id=`s37`、id=`s-qa`
- **浅色 logo**（深色版本）：其余所有内容页

### data-build 渐进展示（可选）
在 `<section>` 上添加 `data-build="N"` 可控制渐进式显示步骤数。每次按下翻页键只显示下一个 block，适合需要互动停顿的页面。

```html
<section class="slide" id="s07" data-build="2" data-build-step="0" data-notes="…">
  <!-- 第一次翻到此页显示 block1 -->
  <section class="s7-block">...</section>
  <!-- 再按一次显示 block2 -->
  <section class="s7-block">...</section>
</section>
```
