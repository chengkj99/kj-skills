# WeChat Media Archive Notes

## MediaCrawler Boundary

Use `NanmiCoder/MediaCrawler` as the workflow reference: login, crawl, save raw JSONL, then run a deterministic merge/report script. The open-source platform list historically covers Douyin/XHS/Bilibili/Kuaishou/Weibo/Tieba/Zhihu and may not include WeChat Official Account or Channels. Always inspect the local checkout before assuming WeChat support.

Recommended probe from a MediaCrawler checkout:

```bash
rg -n "wechat|weixin|wx|gzh|mp|channels|shipin|video_account" .
uv run main.py --help
```

If a current checkout exposes a WeChat platform, keep its raw output under the matching run directory and then run `update_wechat_archive.py`.

## Preferred Archive Roots

- 公众号: `raw/studio/funnel/published/wechat/`
- 视频号: `raw/studio/funnel/published/shipinhao/`

Keep run snapshots by date. Do not overwrite older runs.

## Export/Input Formats

The normalization script accepts JSONL, CSV, and Markdown files under `runs/YYYY-MM-DD/`.

Common work/article/video fields:

- ID: `id`, `item_id`, `article_id`, `video_id`, `comment_id`, `msgid`, `content_id`
- title: `title`, `name`, `desc`, `content`, `digest`
- URL: `url`, `link`, `article_url`, `video_url`, `source_url`
- time: `publish_time`, `create_time`, `created_at`, `time`, `date`
- metrics: `read_count`, `view_count`, `like_count`, `liked_count`, `comment_count`, `share_count`, `favorite_count`, `collect_count`

Common comment/message fields:

- comment ID: `comment_id`, `id`, `reply_id`
- parent item ID: `item_id`, `article_id`, `video_id`, `content_id`, `msgid`
- nickname: `nickname`, `user_name`, `author`, `comment_user`
- text: `content`, `comment`, `text`, `message`
- like count: `like_count`, `liked_count`

If a file name contains `comment`, `留言`, `评论`, or `reply`, rows are treated as comments. Other rows are treated as works/articles/videos unless they have obvious comment-only fields.

## 公众号 Manual Export Workflow

Use this when MediaCrawler cannot crawl 公众号:

1. Open WeChat Official Account backend in Chrome with the user's login.
2. Export article list and available metrics where permitted.
3. Export or copy selected public comments/messages if available.
4. Save files under `raw/studio/funnel/published/wechat/runs/YYYY-MM-DD/exports/`.
5. Run `update_wechat_archive.py --platform wechat`.

Suggested run notes:

```markdown
# Run Notes

- Source: WeChat Official Account backend manual export
- Scope: articles/comments available on YYYY-MM-DD
- Limitations: ...
```

## 视频号 Manual Export Workflow

Use this when MediaCrawler cannot crawl 视频号:

1. Open Channels backend/creator center in Chrome with the user's login.
2. Export visible video list and metrics, or copy a table into CSV/Markdown.
3. Export public comments where permitted.
4. Save files under `raw/studio/funnel/published/shipinhao/runs/YYYY-MM-DD/exports/`.
5. Run `update_wechat_archive.py --platform shipinhao`.

## Report Semantics

- Full ledger: complete run-level table and comments/messages.
- Review analysis: metric rankings, comment categories, and next review actions.
- Latest summary: manifest-level snapshot for `$content-growth-review`.

For growth planning, do not stop after this skill. Run `$content-growth-review` with the latest generated summaries.
