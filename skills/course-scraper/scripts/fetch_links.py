#!/usr/bin/env python3
"""链接清单模式 (link-list / batch fetch)。

适用于「一份包含许多异构链接的清单」（导航页、资源合集、Markdown 链接表），
而不是单一登录课程平台（那种用 scrape.py）。

对每个 URL：Playwright 渲染（应对 SPA）→ 优先定位正文容器并保留图片原位
→ trafilatura / markdownify 兜底 → 写入一个 .md 文件，并在文件头标注来源与质量。
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
import sys, re, json, time, argparse, hashlib, mimetypes
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import trafilatura
from markdownify import markdownify as md

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
URL_RE = re.compile(r"https?://[^\s)\]|<>\"']+")
CONTENT_SELECTORS = [
    "article",
    "main",
    "[role='main']",
    ".markdown-body",
    ".post-content",
    ".entry-content",
    ".article-content",
    ".article__content",
    ".article-body",
    ".content-body",
    ".lesson-content",
    ".course-content",
    "#lesson-content",
    ".lesson-body",
    ".main-content",
    "#js_content",
]
NOISE_LINE_PATTERNS = [
    r"^(read more|read original|continue reading|view original)$",
    r"^(share|tweet|copy link|subscribe|sign up|log in|login)$",
    r"^(comments?|leave a comment|write a comment|写留言|暂无留言)$",
    r"^(related posts?|recommended|you may also like|相关阅读|相关文章|推荐阅读)$",
    r"^(previous|next|上一篇|下一篇)$",
    r"^(扫码|扫一扫|scan .*code).*$",
    r"^[-—\s]*(往期文章分享|相关阅读|相关文章|推荐阅读)[-—\s]*$",
    r"^△\s*点开看大图$",
    r"^,$",
]
CTA_KEYWORDS = {
    "readmore",
    "readoriginal",
    "continuereading",
    "vieworiginal",
    "subscribe",
    "signup",
    "login",
    "comments",
    "writeacomment",
    "写留言",
    "暂无留言",
    "往期文章分享",
    "相关阅读",
    "相关文章",
    "推荐阅读",
}


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


def clean_markdown_noise(body):
    lines = []
    noise_res = [re.compile(p, re.IGNORECASE) for p in NOISE_LINE_PATTERNS]
    skip_next_link = False
    for raw_line in (body or "").splitlines():
        line = raw_line.strip()
        plain = re.sub(r"[*_`~\s\-—:：]+", "", line).lower()
        is_noise = (
            any(p.search(line) for p in noise_res)
            or plain in CTA_KEYWORDS
            or (plain.startswith("觉得") and ("赞" in plain or "在看" in plain))
            or (plain.startswith("please") and ("share" in plain or "subscribe" in plain))
        )
        if skip_next_link and re.match(r"^\[[^\]]+\]\([^)]+\)$", line):
            skip_next_link = False
            continue
        skip_next_link = False
        if is_noise:
            if plain in {"往期文章分享", "相关阅读", "相关文章", "推荐阅读", "relatedposts", "youmayalsolike"}:
                skip_next_link = True
            continue
        lines.append(raw_line.rstrip())
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def extract_container_html(page):
    return page.evaluate(
        """(selectors) => {
            const cloneForMarkdown = (node) => {
                const root = node.cloneNode(true);
                root.querySelectorAll([
                    'script', 'style', 'noscript', 'iframe', 'form',
                    'nav', 'header', 'footer', 'aside',
                    '[aria-hidden="true"]', '[hidden]',
                    '.comment', '.comments', '.reply', '.replies',
                    '.share', '.share-area', '.share_area',
                    '.social', '.social-share', '.newsletter',
                    '.subscribe', '.subscription', '.promo',
                    '.advertisement', '.ad', '.ads',
                    '.qr_code', '.qrcode', '.qr-code',
                    '.author-card', '.author-box', '.profile-card'
                ].join(',')).forEach((el) => el.remove());
                for (const img of root.querySelectorAll('img')) {
                    const src =
                        img.getAttribute('data-src') ||
                        img.getAttribute('data-original') ||
                        img.getAttribute('data-lazy-src') ||
                        img.currentSrc ||
                        img.getAttribute('src') ||
                        '';
                    if (!src || src.startsWith('data:') || src.startsWith('blob:')) {
                        img.remove();
                        continue;
                    }
                    let url;
                    try { url = new URL(src, document.baseURI).href; } catch { img.remove(); continue; }
                    img.setAttribute('src', url);
                    if (!img.getAttribute('alt')) {
                        img.setAttribute('alt', img.getAttribute('title') || 'image');
                    }
                    img.removeAttribute('srcset');
                    img.removeAttribute('data-src');
                    img.removeAttribute('data-original');
                    img.removeAttribute('data-lazy-src');
                }
                return root;
            };

            const candidates = [];
            for (const [index, selector] of selectors.entries()) {
                for (const node of document.querySelectorAll(selector)) {
                    const text = (node.innerText || '').replace(/\\s+/g, ' ').trim();
                    const images = node.querySelectorAll('img').length;
                    if (text.length < 80 && images === 0) continue;
                    const selectorPenalty = selector === 'body' ? 100000 : 0;
                    const selectorBonus = Math.max(0, selectors.length - index) * 1000;
                    const linkPenalty = Math.min(node.querySelectorAll('a').length * 10, 500);
                    candidates.push({
                        selector,
                        textLength: text.length,
                        images,
                        score: text.length + images * 120 + selectorBonus - linkPenalty - selectorPenalty,
                        node
                    });
                }
            }
            if (!candidates.length) {
                candidates.push({
                    selector: 'body',
                    textLength: (document.body.innerText || '').length,
                    images: document.body.querySelectorAll('img').length,
                    score: 0,
                    node: document.body
                });
            }
            candidates.sort((a, b) => b.score - a.score);
            const best = candidates[0];
            return {
                selector: best.selector,
                html: cloneForMarkdown(best.node).innerHTML,
                textLength: best.textLength,
                images: best.images
            };
        }""",
        CONTENT_SELECTORS + ["body"],
    )


def extract_md(html, url):
    txt = trafilatura.extract(
        html, output_format="markdown", include_links=True, include_images=True, include_tables=True,
        include_comments=False, include_formatting=True, favor_recall=True, url=url)
    if txt and len(txt.strip()) > 120:
        return clean_markdown_noise(txt), "trafilatura"
    try:
        body = md(html, heading_style="ATX",
                  strip=["script", "style", "nav", "footer", "header"])
        return clean_markdown_noise(body), "markdownify-fallback"
    except Exception:
        return clean_markdown_noise(txt or ""), "trafilatura-thin"


def extract_page_md(page, url):
    container = extract_container_html(page)
    body = md(container["html"], heading_style="ATX",
              strip=["script", "style", "nav", "footer", "header"])
    body = clean_markdown_noise(body)
    if len(body.strip()) > 120:
        return body, f"dom-container:{container['selector']}", container["selector"]
    body, method = extract_md(page.content(), url)
    return body, method, ""


def hydrate_lazy_content(page):
    """触发懒加载图片/正文块，避免只抓到首屏。"""
    try:
        page.evaluate(
            """async () => {
                const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
                const total = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
                for (let y = 0; y <= total; y += 900) {
                    window.scrollTo(0, y);
                    await sleep(120);
                }
                window.scrollTo(0, 0);
                await sleep(300);
            }"""
        )
    except Exception:
        pass


def ext_from_response(url, content_type):
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    ext = mimetypes.guess_extension(ctype) if ctype else ""
    if ext == ".jpe":
        ext = ".jpg"
    if ext:
        return ext
    path_ext = Path(urlparse(url).path).suffix.lower()
    if path_ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}:
        return path_ext
    return ".bin"


def is_image_response(content_type):
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    return ctype.startswith("image/") or ctype == "image/svg+xml"


def slug_text(text, fallback):
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", (text or "").strip()).strip("-").lower()
    return (text or fallback)[:48]


def collect_image_candidates(page, root_selector=""):
    return page.evaluate("""({rootSelector, selectors}) => {
        let root = null;
        if (rootSelector) root = document.querySelector(rootSelector);
        if (!root) {
            for (const selector of selectors) {
                root = document.querySelector(selector);
                if (root && ((root.innerText || '').trim().length > 80 || root.querySelector('img'))) break;
            }
        }
        root = root || document.body;
        const nodes = Array.from(root.querySelectorAll('img'));
        const out = [];
        const seen = new Set();
        for (const img of nodes) {
            const src =
                img.getAttribute('data-src') ||
                img.getAttribute('data-original') ||
                img.getAttribute('data-lazy-src') ||
                img.currentSrc ||
                img.src ||
                img.getAttribute('src') ||
                '';
            if (!src || src.startsWith('data:') || src.startsWith('blob:')) continue;
            let url;
            try { url = new URL(src, document.baseURI).href; } catch { continue; }
            if (seen.has(url)) continue;
            seen.add(url);
            const rect = img.getBoundingClientRect();
            const width = Math.round(img.naturalWidth || rect.width || 0);
            const height = Math.round(img.naturalHeight || rect.height || 0);
            if ((width && width < 32) || (height && height < 32)) continue;
            out.push({
                url,
                alt: img.getAttribute('alt') || img.getAttribute('title') || '',
                width,
                height
            });
        }
        return out;
    }""", {"rootSelector": root_selector, "selectors": CONTENT_SELECTORS})


def download_images(ctx, page, target_dir, page_slug, root_selector="", max_images=80):
    candidates = collect_image_candidates(page, root_selector)[:max_images]
    asset_dir = target_dir / "_assets" / page_slug
    downloaded = []
    seen_hashes = set()
    for img in candidates:
        url = img["url"]
        fetch_url = url.split("#", 1)[0]
        try:
            response = ctx.request.get(fetch_url, timeout=20000, headers={"Referer": page.url, "User-Agent": UA})
            if not response.ok:
                img["error"] = f"HTTP {response.status}"
                continue
            content_type = response.headers.get("content-type", "")
            if not is_image_response(content_type):
                img["error"] = f"non-image {content_type or 'unknown'}"
                continue
            body = response.body()
            if not body:
                img["error"] = "empty"
                continue
            digest = hashlib.sha256(body).hexdigest()
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            asset_dir.mkdir(parents=True, exist_ok=True)
            ext = ext_from_response(fetch_url, content_type)
            name = f"{len(downloaded) + 1:02d}-{slug_text(img.get('alt'), 'image')}{ext}"
            path = asset_dir / name
            path.write_bytes(body)
            img["local"] = f"_assets/{page_slug}/{name}"
            downloaded.append(img)
        except Exception as exc:
            img["error"] = str(exc)[:120]
            continue
    return downloaded, len(candidates)


def localize_markdown_images(body, images):
    body = body or ""
    for img in images:
        local = img.get("local")
        if not local:
            continue
        remote_urls = {img["url"], img["url"].split("#", 1)[0]}
        for remote_url in remote_urls:
            remote = re.escape(remote_url)
            body = re.sub(rf"!\[([^\]]*)\]\({remote}(?:\s+\"[^\"]*\")?\)", rf"![\1]({local})", body)
            body = body.replace(remote_url, local)
        body = re.sub(rf"(\({re.escape(local)})#[^)]+(\))", rf"\1\2", body)
    return body


def append_image_gallery(body, images):
    if not images:
        return body
    if any(img.get("local") and img["local"] in (body or "") for img in images):
        return body
    lines = ["", "## 图片 / Images", ""]
    for img in images:
        if not img.get("local"):
            continue
        alt = img.get("alt") or "image"
        lines.append(f"![{alt}]({img['local']})")
        lines.append("")
    return (body or "").rstrip() + "\n" + "\n".join(lines).rstrip() + "\n"


def is_bad_extraction(body, method):
    text = body or ""
    lower = text.lower()
    blocked_markers = [
        "环境异常",
        "完成验证后即可继续访问",
        "security verification",
        "captcha",
        "verify.html",
        "access denied",
        "enable javascript",
    ]
    if any(marker in lower or marker in text for marker in blocked_markers):
        return True
    if method == "markdownify-fallback":
        css_js_markers = ["@media(", "function ", "window.", "document.", "var ", "const "]
        if sum(marker in text for marker in css_js_markers) >= 3:
            return True
    return False


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
                hydrate_lazy_content(page)
                time.sleep(0.8)
                body, method, root_selector = extract_page_md(page, url)
                n = len((body or "").strip())
                target_dir = out_root / subdir if subdir else out_root
                target_dir.mkdir(parents=True, exist_ok=True)
                fpath = target_dir / f"{idx:02d}-{slug}.md"
                page_slug = f"{idx:02d}-{slug}"
                images, image_candidates = download_images(ctx, page, target_dir, page_slug, root_selector=root_selector)
                body = append_image_gallery(localize_markdown_images(body, images), images)
                bad = is_bad_extraction(body, method)
                flag = "OK" if n > 120 and not bad else "THIN"
                header = (f"# {title}\n\n> 来源 / Source: {url}\n"
                          f"> 抓取方式: Playwright + {method} | 字符数: {n} | 状态: {flag}\n"
                          f"> 图片 / Images: {len(images)}/{image_candidates}\n\n---\n\n")
                fpath.write_text(header + (body or "_[空 / empty —— 建议 WebFetch 兜底]_"), encoding="utf-8")
                rec.update({"ok": flag == "OK", "chars": n, "method": method,
                            "root_selector": root_selector,
                            "bad_extraction": bad,
                            "images": len(images), "image_candidates": image_candidates,
                            "file": str(fpath.relative_to(out_root))})
                print(f"[{idx:02d}] {flag:<4} {n:>7}c  img {len(images):>2}/{image_candidates:<2}  {method:<22} {url}")
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
