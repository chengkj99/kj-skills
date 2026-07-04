# MediaCrawler Notes

Use `NanmiCoder/MediaCrawler` for Douyin creator crawling. The working pattern for this account is:

- platform: `dy`
- login type: `qrcode`
- crawler type: `creator`
- save option: `jsonl`
- comments: enabled
- sub-comments: disabled
- per-work comment cap: `500`
- concurrency: `1`

The first successful run on 2026-07-05 found 119 visible works and 4012 first-level comments.

Important behavior:

- Creator crawls write works to `creator_contents_YYYY-MM-DD.jsonl`.
- Comments write to `creator_comments_YYYY-MM-DD.jsonl`.
- The crawler may expose media download URLs in JSONL even when media files are not downloaded.
- Keep raw JSONL snapshots. Downstream reports should be regenerated from JSONL rather than edited by hand.
