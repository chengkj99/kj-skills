# WeChat API Safety Notes

Use this reference when saving a Markdown article to a WeChat Official Account draft, especially after `draft/add` rejects content.

## Common Rejection Pattern

`45166 invalid content hint` can be triggered by content shape, not only by forbidden words. In this workflow, a successful fix was:

- Remove generated Markdown table-of-contents anchor lists.
- Remove external reference links before API publishing.
- Remove or rewrite hard follow/subscribe CTAs.
- Keep the follow CTA natural, short, and link-free.
- Keep the cover image as the API `thumb_media_id`, not an inline Markdown image unless the article needs it.

## Safer Structure

Prefer:

```markdown
## 前言
## 一、...
### （一）...
### （二）...
## 二、...
## 写在最后
```

Avoid for WeChat API publishing:

```markdown
## 目录
- [第一章...](#第一章...)
- [1.1...](#1.1...)

## 参考资料
- [external site](https://example.com)
```

Internal anchors and footnote-like citations can expand into many links in generated HTML and increase rejection risk.

## Retry Checklist

1. Run the publishing tool dry run and note `contentLength`.
2. Search the publish copy for `http`, `https`, `](`, `目录`, `二维码`, `扫码`, `关注`.
3. Remove or rewrite risky sections.
4. Retry API publishing.
5. If the retry succeeds, report the new `media_id` and tell the user which draft to use.

## Natural CTA Template

```markdown
## 写在最后

如果你也在用 Claude Code、Codex、Cursor，或者正在把 AI 编程接进自己的真实项目里，我会继续把这些工具、工作流和踩坑经验整理成更容易上手的教程。

欢迎关注我的公众号「程序员AI破局指南」。后面我会继续写 Agent Skills、AI 编程工作流、项目实战和个人工具链搭建，不只讲概念，更希望帮你把 AI 真正用进每天的开发和产品构建里。
```
