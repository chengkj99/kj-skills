#!/usr/bin/env python3
"""链接清单模式 (link-list / batch fetch)。

适用于「一份包含许多异构链接的清单」（导航页、资源合集、Markdown 链接表），
而不是单一登录课程平台（那种用 scrape.py）。

对每个 URL：Playwright 渲染（应对 SPA）→ trafilatura 主内容提取为 Markdown
→ markdownify 兜底 → 写入一个 .md 文件，并在文件头标注来源与质量。
被反爬/JS 营销页/付费墙挡住的（输出过短或报错）会标为 THIN/ERROR，
留给调用方（Agent）用 WebFetch 工具二次兜底（WebFetch 是 Agent 工具，脚本内无法调用）。

依赖：playwright、trafilatura、markdownify
  pip3 install playwright trafilatura markdownify && python3 -m playwright install chromium

用法：
  python3 fetch_links.py --links <清单文件> --output <输出目录> [--subdir <子目录>] [--limit N]

清单文件支持两种格式：
  1) .json —— [{"subdir","idx","slug","title","url"}, ...]
  2) 其它（.md/.txt）—— 自动抽取所有 https?:// 链接；若是 Markdown 表格行，
     取 URL 前第一个非空单元格作为标题；slug 由 URL 路径自动生成。
"""
import sys, re, json, time, argparse
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import trafilatura
from markdownify import markdownify as md

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
URL_RE = re.compile(r"https?://[^\s)\]|<>\"']+")


def slugify(url):
    p = urlparse(url)
    parts = [seg for seg in p.path.split("/") if seg]
    base = "-".join(parts[-2:]) if parts else p.netloc
    base = re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-").lower()
    return (base or p.netloc.replace(".", "-"))[:60]


def parse_links(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text)
    items, seen = [], set()
    for line in text.splitlines():
        for m in URL_RE.finditer(line):
            url = m.group(0).rstrip(".,);")
            if url in seen:
                continue
            seen.add(url)
            title = ""
            if line.lstrip().startswith("|"):  # markdown table row
                cells = [c.strip().strip("*`[]") for c in line.split("|")]
                cells = [c for c in cells if c and "http" not in c]
                title = cells[0] if cells else ""
            items.append({"subdir": "", "idx": len(items) + 1,
                          "slug": slugify(url), "title": title or slugify(url), "url": url})
    return items


def extract_md(html, url):
    txt = trafilatura.extract(
        html, output_format="markdown", include_links=True, include_tables=True,
        include_comments=False, include_formatting=True, favor_recall=True, url=url)
    if txt and len(txt.strip()) > 120:
        return txt, "trafilatura"
    try:
        body = md(html, heading_style="ATX",
                  strip=["script", "style", "nav", "footer", "header"])
        return body, "markdownify-fallback"
    except Exception:
        return (txt or ""), "trafilatura-thin"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--links", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--subdir", default="")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    out_root = Path(args.output)
    items = parse_links(args.links)
    if args.limit:
        items = items[: args.limit]

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 1800})
        page = ctx.new_page()
        for it in items:
            subdir = args.subdir or it.get("subdir", "")
            idx, slug, title, url = it["idx"], it["slug"], it.get("title", it["slug"]), it["url"]
            rec = {"idx": idx, "slug": slug, "title": title, "url": url, "subdir": subdir}
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                try:
                    page.wait_for_load_state("networkidle", timeout=12000)
                except Exception:
                    pass
                time.sleep(1.2)
                body, method = extract_md(page.content(), url)
                n = len((body or "").strip())
                target_dir = out_root / subdir if subdir else out_root
                target_dir.mkdir(parents=True, exist_ok=True)
                fpath = target_dir / f"{idx:02d}-{slug}.md"
                flag = "OK" if n > 120 else "THIN"
                header = (f"# {title}\n\n> 来源 / Source: {url}\n"
                          f"> 抓取方式: Playwright + {method} | 字符数: {n} | 状态: {flag}\n\n---\n\n")
                fpath.write_text(header + (body or "_[空 / empty —— 建议 WebFetch 兜底]_"), encoding="utf-8")
                rec.update({"ok": n > 120, "chars": n, "method": method,
                            "file": str(fpath.relative_to(out_root))})
                print(f"[{idx:02d}] {flag:<4} {n:>7}c  {method:<22} {url}")
            except Exception as e:
                rec.update({"ok": False, "chars": 0, "method": "ERROR", "error": str(e)[:200]})
                print(f"[{idx:02d}] ERR  {url}\n      {str(e)[:160]}")
            results.append(rec)
        browser.close()

    (out_root / "_fetch_report.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in results if r.get("ok"))
    thin = sum(1 for r in results if not r.get("ok") and r.get("method") != "ERROR")
    err = sum(1 for r in results if r.get("method") == "ERROR")
    print(f"\n=== DONE: {ok} ok / {thin} thin / {err} error / {len(results)} total ===")
    print("THIN/ERROR 的链接请用 WebFetch 工具二次兜底（并在文件头标注「非逐字原文」）。")


if __name__ == "__main__":
    main()
