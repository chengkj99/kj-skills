---
name: kangjian-wechat-media
description: Archive and analyze 程序员康健 WeChat Official Account and WeChat Channels media data. Use when the user asks to crawl, import, update, or review 公众号文章、视频号作品、微信评论/留言, or maintain raw/studio/funnel/published/wechat and raw/studio/funnel/published/shipinhao snapshots.
---

# Kangjian WeChat Media

Use this skill to maintain the user's WeChat ecosystem media archive:

- Display identity: `程序员康健`
- Platforms:
  - WeChat Official Account / 公众号: archive root `raw/studio/funnel/published/wechat/`
  - WeChat Channels / 视频号: archive root `raw/studio/funnel/published/shipinhao/`

This skill mirrors `$kangjian-douyin-media`: keep immutable run snapshots, merge incrementally into a manifest, then generate Markdown reports for review and later `$content-growth-review`.

## Capability Boundary

Open-source `NanmiCoder/MediaCrawler` does not currently expose a stable 公众号/视频号 crawler in the same way it supports Douyin. Treat MediaCrawler as a pattern and first check whether the local checkout has added WeChat support. If not, use authenticated Chrome/manual export or a user-provided export file, then normalize it with `scripts/update_wechat_archive.py`.

Read `references/wechat-media.md` when you need the exact run options, export-field expectations, or fallback workflow.

## Update Cadence

- New post/video: import after 24 hours for first feedback.
- Review window: import again after 3-7 days.
- Baseline refresh: import the full visible account monthly or quarterly.

Do not download media files by default. Do not scrape private user data beyond public/authorized comments or message exports. Preserve each run under a date-stamped directory.

## Run Snapshot Contract

Store each run under:

```text
raw/studio/funnel/published/<platform>/runs/YYYY-MM-DD/
  exports/
    *.jsonl
    *.csv
    *.md
  notes.md
```

Use `<platform>` as:

- `wechat` for 公众号
- `shipinhao` for 视频号

If MediaCrawler or another tool writes platform-specific JSONL folders, keep them under the same `runs/YYYY-MM-DD/` directory; the normalization script will recursively scan supported files.

## Incremental Merge

After obtaining a run snapshot, run:

```bash
python3 <skill_dir>/scripts/update_wechat_archive.py \
  --archive-dir "<wiki>/raw/studio/funnel/published/wechat" \
  --run-dir "<wiki>/raw/studio/funnel/published/wechat/runs/YYYY-MM-DD" \
  --date "YYYY-MM-DD" \
  --platform wechat \
  --account "kangjian-wechat"
```

For 视频号:

```bash
python3 <skill_dir>/scripts/update_wechat_archive.py \
  --archive-dir "<wiki>/raw/studio/funnel/published/shipinhao" \
  --run-dir "<wiki>/raw/studio/funnel/published/shipinhao/runs/YYYY-MM-DD" \
  --date "YYYY-MM-DD" \
  --platform shipinhao \
  --account "kangjian-shipinhao"
```

The script will:

- read JSONL, CSV, or Markdown exports under the run directory
- infer works/articles/videos and comments/messages using common field names
- update `manifest/<account>-manifest.json`
- create `YYYY-MM-DD-<account>-<platform>-full-ledger.md`
- create `YYYY-MM-DD-<account>-<platform>-review-analysis.md`
- refresh `latest-<account>-summary.md`

Use `--full-refresh` when the run intentionally covers the full account/channel history.

## Output Contract

```text
raw/studio/funnel/published/<platform>/
  manifest/
    <account>-manifest.json
  runs/
    YYYY-MM-DD/
      exports/
        ...
  YYYY-MM-DD-<account>-<platform>-full-ledger.md
  YYYY-MM-DD-<account>-<platform>-review-analysis.md
  latest-<account>-summary.md
```

The manifest is the incrementally maintained index. Run snapshots remain auditable inputs and should not be overwritten.

## Downstream Review

After updating the archive, use `$content-growth-review` for:

- cross-platform growth diagnosis
- topic direction adjustment
- comment/message insight mining
- topic pool generation under `raw/studio/funnel/backlog/manual/`

Use `$local-stt-transcription` only for downloaded 视频号 files when a transcript is needed; this skill should only link transcript paths, not create transcripts.

## Validation

Before reporting completion:

1. Report how the data was obtained: MediaCrawler support, Chrome/manual export, or user-provided files.
2. Run the archive update script and report `items`, `comments`, `new_items`, and `new_comments`.
3. Run `git diff --check -- raw/studio/funnel/published/wechat raw/studio/funnel/published/shipinhao` when those paths exist.
4. Mention whether the run was incremental or full refresh and whether any field mapping was partial.

## Failure Handling

- If the local MediaCrawler checkout lacks WeChat support, say so and switch to export/import mode.
- If Chrome login is required, ask the user to approve WeChat login/QR scanning.
- If exports lack stable IDs, the script will generate deterministic IDs from title/time/url; mention that future deduplication may be weaker.
- If comments/messages are rate-limited or hidden by platform permissions, keep the run as partial and schedule a later refresh.
