---
name: wechat-publish-kit
description: >-
  Prepare a complete WeChat Official Account article release package from an existing article, tutorial, Word/Markdown draft, or source document. Use when the user asks for 公众号发布素材、公众号配套、封面图、发布稿、公众号草稿, or wants to turn an article into a publish-ready WeChat package with generated cover image, companion copy, publish-safe Markdown, title-selection handoff, and optional draft publishing. 这是公众号发布的默认总控入口；若用户明确只要标题/前言/摘要/转发文案等纯文案物料、不需要生成封面图片和发布稿，改用 wechat-companion。
---

# WeChat Publish Kit

把一篇文章从“正文已写好”推进到“可以发公众号”：生成配套文案、自动生成封面图、打包发布用 Markdown，引导用户从备选标题中选择一个标题，并在标题确认后继续把标题、正文、封面图片、摘要简介保存为公众号草稿。

## Direct-publish shortcut

用户已经给出最终标题，或直接说“发布到公众号草稿箱 / 保存草稿 / 用 API 发布”时，不再要求他重新选择标题，直接进入发布流程；但不能跳过封面生成、摘要检查和 API dry run。

直接发布仍按以下顺序执行：

1. 检查最终标题、正文与摘要；
2. 解析封面路径并执行封面预检；
3. 没有合格封面时自动生成；
4. 运行 API dry run；
5. 创建新草稿，或使用已知 `media_id` 更新原草稿。

## Core Workflow

1. **Read the source article**
   - Prefer the canonical source the user points to: `.md`, `.docx`, or an existing article draft.
   - If both Word and Markdown exist, use Markdown for automated publishing and treat Word as the human-facing version unless the user says otherwise.
   - Extract the article positioning, target reader, pain point, concrete promise, and any existing title/frontmatter.
   - If the source already has a strong title, keep it as one of the title options instead of silently replacing it.

2. **Generate companion materials**
   - Article intro: 150-300 Chinese characters, reader-pain first, no “本文将介绍”.
   - 5 title options unless the user has already chosen one.
   - Summary: under 120 Chinese characters for WeChat digest / social preview.
   - Cover prompt: English, explicit 2.35:1 / `--ar 47:20`, with subject-specific visual elements.
   - Cover image path: `raw/studio/funnel/formatted/wechat/assets/<yyyy-mm-dd-slug>/cover.png`.
   - Forward copy: one Moments version and one AI practice group version.
   - Companion file must include:
     - source article path
     - publish copy path
     - chosen-title status: `待选择` until user confirms
     - generated cover image path
     - cover prompt
     - title options
     - summary
     - article intro
     - forward copy

3. **Generate the cover image by default**
   - Default behavior: generate a usable cover image, not only a prompt。即使用户直接要求发布草稿、没有经过标题选择环节，也必须执行本步骤。
   - Resolve the cover in this order:
     1. 用户明确指定的封面；
     2. 当前文章资产目录里已经存在且尺寸合格的 `cover.png`；
     3. 根据最终标题、文章核心冲突和读者对象自动生成的新封面。
   - 正文首图、数据图或流程图不自动等同于封面。只有用户明确指定，或它本身就是已验证的 2.35:1 封面时才能复用，避免发布脚本静默采用正文第一张图。
   - Use the image generation tool after drafting the cover prompt.
   - Store the final usable cover under the article’s WeChat asset folder:
     `raw/studio/funnel/formatted/wechat/assets/<yyyy-mm-dd-slug>/cover.png`.
   - If the generated image is returned outside the workspace, copy or move the final selected image into the asset folder.
   - Verify the file exists and inspect image metadata with `file`, `sips -g pixelWidth -g pixelHeight`, or an equivalent metadata command.
   - Generate a wide composition close to 2.35:1, then normalize the final file to `900 × 383` when local image tooling is available. Keep the subject and visual conflict inside the safe center area so desktop and mobile crops both work.
   - 默认不把文章长标题画进图片，避免错字和移动端缩小后不可读；公众号标题栏会承载文字。只有用户明确要求“封面带字”时才生成文字版。
   - 封面要表达文章的核心冲突或结果，不要只堆 AI Logo、机器人、代码雨或通用科技元素。
   - Only skip image generation when the user explicitly says “只要提示词 / 不生成图片 / no image”.
   - If image generation is unavailable, keep the cover prompt and mark the companion file `cover_status: 未生成（缺少可用图像生成工具）`; do not pretend a cover exists.
   - Before publishing, verify:
     - `cover.png` exists;
     - dimensions are `900 × 383` or aspect ratio is close to 2.35:1;
     - frontmatter `cover` resolves to this file;
     - API receives this file as its thumb/cover argument.

4. **Create a publish-ready Markdown copy**
   - Do not modify the canonical source article unless explicitly asked.
   - Create a publish copy under `raw/studio/funnel/formatted/wechat/`.
   - Add frontmatter: `title`, `author`, `date`, `summary`, and `cover`.
   - Before the user chooses a title, use the recommended/default title in frontmatter and H1, and mark the companion file as waiting for confirmation.
   - After the user chooses a title, update both frontmatter `title` and H1 to exactly that title.
   - Keep the publish copy WeChat-safe:
     - Remove generated table-of-contents anchor lists.
     - Prefer top-level sections like `一、二、三...` over “第 X 章” for public articles.
     - Prefer subheads like `（一）（二）` over `1.1 / 1.2` when the article should feel less like courseware.
     - Remove or minimize external links before API publishing unless the user explicitly wants them.
     - Keep follow/CTA text natural, short, and link-free.
     - Do not inline the cover image in the article body unless the user explicitly wants it; the cover should normally be used as the WeChat API thumb image.

5. **Ask the user to choose a title**
   - Stop after the first packaging pass and present only:
     - the 5 title options
     - recommended option
     - publish copy path
     - cover image path
     - summary
     - a concise instruction: “回复标题序号或直接给新标题；确认后我会继续保存公众号草稿。”
   - Do not ask for more information unless publishing cannot proceed without it.
   - Treat the user’s reply with a title number, title text, or explicit “用第 N 个” as approval to continue the publishing flow.
   - If the user provides a new title, use that title exactly unless it is too long or unsafe for WeChat; if so, propose one tightened version and ask once.

6. **Continue publishing after title confirmation**
   - Update the publish copy title/H1 and companion file chosen-title status.
   - Ensure the package has the final chosen title, final summary, final cover image path, and publish-safe Markdown.
   - Use the `baoyu-post-to-wechat` skill/tooling if available.
   - Prefer API publishing for Markdown drafts when credentials are configured.
   - Always run a dry run first if the workflow supports it.
   - Run a cover preflight immediately before the API call. If the cover path is empty, missing, points to a body image by fallback, or has an unsuitable aspect ratio, return to step 3 and generate the cover before publishing.
   - Do not rely on the publisher’s “use first body image as cover” fallback in the normal workflow.
   - Then create or update the WeChat draft with:
     - title: chosen title
     - digest/summary: final summary
     - content: publish-ready Markdown/HTML
     - thumb/cover: generated cover image
   - If WeChat API returns `45166 invalid content`, read `references/wechat-api-safety.md`, clean the publish copy, and retry.
   - If the publishing tool is unavailable or credentials are missing, stop with the package complete and report exactly what is missing.

## Output Locations

For the `kj-llm-wiki` studio workflow, use:

- Publish-ready article: `raw/studio/funnel/formatted/wechat/<yyyy-mm-dd-slug>-publish.md`
- Companion materials: `raw/studio/funnel/formatted/wechat/<yyyy-mm-dd-slug>-wechat-companion.md`
- Cover and article assets: `raw/studio/funnel/formatted/wechat/assets/<yyyy-mm-dd-slug>/`
- Generated cover image: `raw/studio/funnel/formatted/wechat/assets/<yyyy-mm-dd-slug>/cover.png`

If the user is outside `kj-llm-wiki`, either follow the current repo’s publishing convention or ask once for the target directory.

## Title Selection Handoff

The first-pass response should be short and action-oriented. Use this shape:

```markdown
已生成发布包，等你选标题后我继续保存公众号草稿。

推荐：2. <title>

1. <title>
2. <title>
3. <title>
4. <title>
5. <title>

- 发布稿：...
- 封面图：...
- 摘要：...

回复标题序号或直接给新标题；确认后我会继续发布流程。
```

After the user chooses, do not repeat the whole package. Continue the draft publishing steps immediately.

## Quality Gates

- Title is concrete and WeChat-readable; avoid vague “完全指南” if the user wants stronger distribution.
- Intro speaks to the reader’s pain before explaining the article.
- Summary is under 120 Chinese characters.
- Cover prompt has `--ar 47:20` or explicitly says 2.35:1.
- Cover image exists at `assets/<yyyy-mm-dd-slug>/cover.png`, unless the user explicitly requested prompt-only mode or image generation is unavailable.
- Cover image is `900 × 383` or close to 2.35:1, and is passed explicitly to the API rather than inferred from the first body image.
- Companion file includes the generated cover image path and title-selection status.
- Publish copy has no Markdown TOC anchor list.
- Publish copy frontmatter cover points to the generated cover image.
- Follow CTA exists when the user expects growth/引流 content, but it does not contain raw external links or QR instructions unless publishing manually.
- After title confirmation, publish copy title and H1 exactly match the chosen title.
- If publishing through API, report the new `media_id` and note if older drafts also exist.

## References

- For WeChat API rejection patterns, formatting risk, and retry steps, read `references/wechat-api-safety.md`.
