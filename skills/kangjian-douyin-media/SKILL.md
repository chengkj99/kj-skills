---
name: kangjian-douyin-media
description: Incrementally crawl, archive, and analyze 程序员康健 / kangjian-douyin Douyin creator media data with MediaCrawler. Use when the user asks to update 程序员康健's Douyin account, crawl new Douyin videos, refresh published Douyin works/comments, generate Douyin full-ledger or review-analysis Markdown reports, or maintain raw/studio/funnel/published/douyin snapshots.
---

# Kangjian Douyin Media

Use this skill to update the user's own Douyin archive for:

- Account: `kangjian-douyin`
- Display identity: `程序员康健`
- Homepage: `https://www.douyin.com/user/MS4wLjABAAAAU0QYHCmBaS2uUvbuc5XfY-XTJJCybRun-GHf2kpR6o0?from_tab_name=main`
- Default archive root in the wiki: `raw/studio/funnel/published/douyin/`

The skill has two layers:

1. Use `NanmiCoder/MediaCrawler` to produce raw Douyin JSONL for works and comments.
2. Run `scripts/update_douyin_archive.py` to merge the run incrementally and generate Markdown reports.

Do not download media files by default. Do not fetch sub-comments by default. Transcripts are produced separately with `$local-stt-transcription` and should be linked under `raw/studio/funnel/transcripts/`.

## Update Cadence

- New video: crawl after 24 hours for first feedback.
- Review window: crawl again after 3-7 days.
- Baseline refresh: crawl the full account monthly or quarterly.

For normal new-video updates, crawl the latest `30-50` works. For audits or drift correction, crawl the full account with a larger cap.

## MediaCrawler Run

Use an existing MediaCrawler checkout if available; otherwise clone it to `/private/tmp/MediaCrawler-kangjian-douyin`.

Recommended command shape:

```bash
uv run main.py \
  --platform dy \
  --lt qrcode \
  --type creator \
  --creator_id "https://www.douyin.com/user/MS4wLjABAAAAU0QYHCmBaS2uUvbuc5XfY-XTJJCybRun-GHf2kpR6o0?from_tab_name=main" \
  --get_comment yes \
  --get_sub_comment no \
  --max_comments_count_singlenotes 500 \
  --crawler_max_notes_count 50 \
  --max_concurrency_num 1 \
  --save_data_option jsonl \
  --save_data_path "<wiki>/raw/studio/funnel/published/douyin/runs/YYYY-MM-DD"
```

Use `--crawler_max_notes_count 130` or higher for a full-account refresh. If login is needed, let the user scan the QR code in Chrome. Keep each run in a date-stamped directory; never overwrite old runs.

## Incremental Merge

After MediaCrawler finishes, run:

```bash
python3 <skill_dir>/scripts/update_douyin_archive.py \
  --archive-dir "<wiki>/raw/studio/funnel/published/douyin" \
  --run-dir "<wiki>/raw/studio/funnel/published/douyin/runs/YYYY-MM-DD" \
  --date "YYYY-MM-DD"
```

The script will:

- read `douyin/jsonl/creator_contents_*.jsonl`
- read `douyin/jsonl/creator_comments_*.jsonl` when present
- update `manifest/kangjian-douyin-manifest.json`
- create `YYYY-MM-DD-kangjian-douyin-douyin-full-ledger.md`
- create `YYYY-MM-DD-kangjian-douyin-douyin-review-analysis.md`
- create or refresh `latest-kangjian-douyin-summary.md`

Use `--full-refresh` when the run intentionally covers the whole account.

## Output Contract

Raw and generated files stay under:

```text
raw/studio/funnel/published/douyin/
  manifest/
    kangjian-douyin-manifest.json
  runs/
    YYYY-MM-DD/
      douyin/jsonl/creator_contents_YYYY-MM-DD.jsonl
      douyin/jsonl/creator_comments_YYYY-MM-DD.jsonl
  YYYY-MM-DD-kangjian-douyin-douyin-full-ledger.md
  YYYY-MM-DD-kangjian-douyin-douyin-review-analysis.md
  latest-kangjian-douyin-summary.md
```

The manifest is the incrementally maintained index. Each run remains an immutable-ish snapshot for auditability.

## Validation

Before reporting completion:

1. Run `wc -l` on contents and comments JSONL.
2. Run the archive update script and report its `works`, `comments`, and `new_works` counts.
3. Run `git diff --check -- raw/studio/funnel/published/douyin`.
4. Mention whether the run was incremental or full refresh, and whether the current visible work count differs from the user's expected count.

## Failure Handling

- If MediaCrawler fails from missing dependencies, run `uv sync` in the checkout and retry.
- If browser or login fails, ask the user to approve Chrome/QR login again.
- If comments are incomplete due to rate limiting, keep the run but say it is partial and rerun later with lower concurrency.
- If the archive path is outside the current writable workspace, request filesystem approval instead of copying data silently.
