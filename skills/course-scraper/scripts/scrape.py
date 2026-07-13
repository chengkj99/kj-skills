#!/usr/bin/env python3
"""
Course Scraper — 课程内容抓取脚本
支持 Skilljar 平台（带登录）及通用网页课程。

用法:
  python3 scrape.py --url <课程URL> --email <邮箱> --password <密码> --output <输出目录>

可选参数:
  --no-login   跳过登录，直接抓取（适用于公开课程）
"""

import argparse
import hashlib
import mimetypes
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


# ── 工具函数 ──────────────────────────────────────────────

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:60]


def goto(page, url: str, timeout: int = 60000):
    page.goto(url, wait_until='domcontentloaded', timeout=timeout)
    time.sleep(2)


def hydrate_lazy_content(page):
    """触发懒加载图片/正文块，避免只抓到首屏。"""
    try:
        page.evaluate("""async () => {
            const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
            const total = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
            for (let y = 0; y <= total; y += 900) {
                window.scrollTo(0, y);
                await sleep(120);
            }
            window.scrollTo(0, 0);
            await sleep(300);
        }""")
    except Exception:
        pass


def detect_platform(url: str) -> str:
    """根据 URL 判断课程平台类型。"""
    host = urlparse(url).netloc.lower()
    if 'skilljar' in host:
        return 'skilljar'
    return 'generic'


# ── 平台登录 ──────────────────────────────────────────────

def login_skilljar(page, base_url: str, course_path: str, email: str, password: str):
    """Skilljar 登录流程：通过 auth/login 触发跳转到 accounts.skilljar.com。"""
    auth_url = f"{base_url}/auth/login?next={course_path}"
    print(f"  触发登录跳转: {auth_url}")
    goto(page, auth_url)

    if 'accounts.skilljar.com' not in page.url:
        print(f"  警告：未跳转到 Skilljar 登录页，当前 URL: {page.url}")
        return False

    print(f"  填写登录表单...")
    page.fill('#id_login', email)
    page.fill('#id_password', password)
    page.click('[type="submit"]')
    time.sleep(3)
    page.wait_for_load_state('domcontentloaded')
    print(f"  登录后 URL: {page.url}")
    return True


def login_generic(page, email: str, password: str) -> bool:
    """通用登录：查找邮箱/密码输入框并提交。"""
    selectors = [
        ('input[type="email"]', 'input[type="password"]'),
        ('input[name="email"]', 'input[name="password"]'),
        ('#email', '#password'),
        ('#user_email', '#user_password'),
    ]
    for email_sel, pass_sel in selectors:
        try:
            if page.query_selector(email_sel):
                page.fill(email_sel, email)
                page.fill(pass_sel, password)
                page.click('[type="submit"], button[type="submit"]')
                time.sleep(3)
                page.wait_for_load_state('domcontentloaded')
                return True
        except Exception:
            continue
    return False


# ── 课时链接收集 ──────────────────────────────────────────

def collect_lesson_links(page, course_slug: str, base_url: str) -> list[dict]:
    """从侧边栏收集所有课时链接。"""
    links = page.evaluate(f"""() => {{
        const results = [];
        for (const a of document.querySelectorAll('a[href]')) {{
            const href = a.getAttribute('href') || '';
            const text = a.innerText.trim();
            if (!href || !text) continue;
            results.push({{ href, title: text }});
        }}
        return results;
    }}""")

    seen = set()
    result = []
    pattern = re.compile(rf'/{re.escape(course_slug)}/\d+$')

    for l in links:
        href = l['href']
        path = href.split('?')[0].split('#')[0]
        if not pattern.search(path):
            continue
        url = href if href.startswith('http') else f"{base_url}{href}"
        clean_url = (base_url + path) if not path.startswith('http') else path
        if clean_url not in seen:
            seen.add(clean_url)
            result.append({'url': clean_url, 'title': l['title']})

    return result


def collect_generic_lesson_links(page, base_url: str) -> list[dict]:
    """通用课时链接收集：查找导航/侧边栏中的链接列表。"""
    links = page.evaluate("""() => {
        const nav = document.querySelector(
            'nav, aside, .sidebar, .course-nav, .lesson-list, [class*="sidebar"], [class*="curriculum"]'
        );
        const container = nav || document.body;
        const results = [];
        for (const a of container.querySelectorAll('a[href]')) {
            const href = a.getAttribute('href') || '';
            const text = a.innerText.trim();
            if (href && text && text.length > 1) {
                results.push({ href, title: text });
            }
        }
        return results;
    }""")

    seen = set()
    result = []
    parsed = urlparse(base_url)
    base_host = f"{parsed.scheme}://{parsed.netloc}"

    for l in links:
        href = l['href']
        url = href if href.startswith('http') else f"{base_host}{href}"
        if url not in seen and urlparse(url).netloc == parsed.netloc:
            seen.add(url)
            result.append({'url': url, 'title': l['title']})

    return result


# ── 内容提取 ──────────────────────────────────────────────

CONTENT_SELECTORS = [
    '.lesson-content', '.course-content', '.content-body',
    '#lesson-content', '.lesson-body', 'article',
    '.main-content', 'main', '[role="main"]'
]


def extract_content(page) -> tuple[str, str]:
    """提取课时正文 Markdown，尽量保留图片在原文中的位置。"""
    try:
        return page.evaluate("""(selectors) => {
            const blockTags = new Set([
                'P', 'DIV', 'SECTION', 'ARTICLE', 'MAIN', 'HEADER', 'FOOTER',
                'UL', 'OL', 'LI', 'PRE', 'BLOCKQUOTE', 'TABLE', 'TR'
            ]);
            const headingTags = new Set(['H1', 'H2', 'H3', 'H4', 'H5', 'H6']);
            const noisySelector = [
                'nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript',
                'iframe', 'form', 'button', '[aria-hidden="true"]', '[hidden]',
                '.sidebar', '.comment', '.comments', '.reply', '.share'
            ].join(',');

            const pickRoot = () => {
                const candidates = [];
                for (const selector of selectors) {
                    for (const node of document.querySelectorAll(selector)) {
                        const text = (node.innerText || '').replace(/\\s+/g, ' ').trim();
                        const images = node.querySelectorAll('img').length;
                        if (text.length < 80 && images === 0) continue;
                        candidates.push({selector, node, score: text.length + images * 120});
                    }
                }
                if (!candidates.length) return {selector: 'body', node: document.body};
                candidates.sort((a, b) => b.score - a.score);
                return candidates[0];
            };

            const normalizeImage = (img) => {
                const src =
                    img.getAttribute('data-src') ||
                    img.getAttribute('data-original') ||
                    img.getAttribute('data-lazy-src') ||
                    img.currentSrc ||
                    img.getAttribute('src') ||
                    '';
                if (!src || src.startsWith('data:') || src.startsWith('blob:')) return '';
                try { return new URL(src, document.baseURI).href; } catch { return ''; }
            };

            const render = (node) => {
                if (node.nodeType === Node.TEXT_NODE) {
                    return (node.textContent || '').replace(/\\s+/g, ' ');
                }
                if (node.nodeType !== Node.ELEMENT_NODE) return '';
                if (node.matches(noisySelector)) return '';
                const tag = node.tagName;
                if (tag === 'IMG') {
                    const src = normalizeImage(node);
                    if (!src) return '';
                    const alt = node.getAttribute('alt') || node.getAttribute('title') || 'image';
                    return `\\n\\n![${alt}](${src})\\n\\n`;
                }
                if (tag === 'BR') return '\\n';
                if (headingTags.has(tag)) {
                    const level = Number(tag.slice(1));
                    const text = Array.from(node.childNodes).map(render).join('').trim();
                    return text ? `\\n\\n${'#'.repeat(level)} ${text}\\n\\n` : '';
                }
                if (tag === 'LI') {
                    const text = Array.from(node.childNodes).map(render).join('').trim();
                    return text ? `\\n- ${text}` : '';
                }
                const inner = Array.from(node.childNodes).map(render).join('');
                if (blockTags.has(tag)) return `\\n\\n${inner.trim()}\\n\\n`;
                return inner;
            };

            const picked = pickRoot();
            const root = picked.node.cloneNode(true);
            root.querySelectorAll(noisySelector).forEach((el) => el.remove());
            const markdown = Array.from(root.childNodes).map(render).join('');
            return {
                markdown: markdown.replace(/\\n{3,}/g, '\\n\\n').trim(),
                selector: picked.selector
            };
        }""", CONTENT_SELECTORS)
    except Exception:
        return "", ""


def ext_from_response(url: str, content_type: str) -> str:
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


def slug_text(text: str, fallback: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", (text or "").strip()).strip("-").lower()
    return (text or fallback)[:48]


def collect_image_candidates(page, root_selector: str = "") -> list[dict]:
    """收集正文区域可见图片 URL，过滤明显图标和 data/blob。"""
    return page.evaluate("""({rootSelector, selectors}) => {
        let container = rootSelector ? document.querySelector(rootSelector) : null;
        if (!container) {
            for (const selector of selectors) {
                container = document.querySelector(selector);
                if (container && ((container.innerText || '').trim().length > 80 || container.querySelector('img'))) break;
            }
        }
        container = container || document.body;
        const out = [];
        const seen = new Set();
        for (const img of container.querySelectorAll('img')) {
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


def is_image_response(content_type: str) -> bool:
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    return ctype.startswith("image/") or ctype == "image/svg+xml"


def download_images(context, page, output_dir: Path, page_slug: str, root_selector: str = "", max_images: int = 80) -> tuple[list[dict], int]:
    candidates = collect_image_candidates(page, root_selector)[:max_images]
    asset_dir = output_dir / "_assets" / page_slug
    downloaded: list[dict] = []
    seen_hashes = set()
    for img in candidates:
        url = img["url"]
        fetch_url = url.split("#", 1)[0]
        try:
            response = context.request.get(fetch_url, timeout=20000, headers={"Referer": page.url})
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
            name = f"{len(downloaded) + 1:02d}-{slug_text(img.get('alt', ''), 'image')}{ext}"
            path = asset_dir / name
            path.write_bytes(body)
            img["local"] = f"_assets/{page_slug}/{name}"
            downloaded.append(img)
        except Exception as exc:
            img["error"] = str(exc)[:120]
    return downloaded, len(candidates)


def localize_markdown_images(content: str, images: list[dict]) -> str:
    content = content or ""
    for img in images:
        local = img.get("local")
        if not local:
            continue
        for remote_url in {img["url"], img["url"].split("#", 1)[0]}:
            remote = re.escape(remote_url)
            content = re.sub(rf"!\[([^\]]*)\]\({remote}(?:\s+\"[^\"]*\")?\)", rf"![\1]({local})", content)
            content = content.replace(remote_url, local)
        content = re.sub(rf"(\({re.escape(local)})#[^)]+(\))", rf"\1\2", content)
    return content


def append_image_gallery(content: str, images: list[dict]) -> str:
    if not images:
        return content
    if any(img.get("local") and img["local"] in (content or "") for img in images):
        return content
    lines = ["", "", "## 图片 / Images", ""]
    for img in images:
        if not img.get("local"):
            continue
        alt = img.get("alt") or "image"
        lines.append(f"![{alt}]({img['local']})")
        lines.append("")
    return content.rstrip() + "\n".join(lines).rstrip() + "\n"


def get_lesson_title(page, sidebar_title: str = "") -> str:
    """获取课时标题，优先用侧边栏标题，其次用页面 h1。"""
    if sidebar_title:
        return sidebar_title

    title = page.evaluate("""() => {
        for (const sel of ['main h1', '.content h1', 'article h1', 'h1']) {
            const el = document.querySelector(sel);
            if (el && el.innerText.trim()) return el.innerText.trim();
        }
        return document.title;
    }""")
    return title or "Untitled"


def get_next_url(page, course_slug: str, base_url: str) -> Optional[str]:
    """获取下一课时的 URL（通过 Next 按钮）。"""
    raw = page.evaluate("""() => {
        for (const a of document.querySelectorAll('a[href]')) {
            const text = a.innerText.trim().toLowerCase();
            const label = (a.getAttribute('aria-label') || '').toLowerCase();
            const href = a.getAttribute('href') || '';
            if ((text === 'next' || label.includes('next')) && href) return href;
        }
        return null;
    }""")
    if not raw:
        return None
    path = raw.split('?')[0].split('#')[0]
    if not re.search(rf'/{re.escape(course_slug)}/\d+', path):
        return None
    return raw if raw.startswith('http') else f"{base_url}{raw}"


# ── 主流程 ────────────────────────────────────────────────

def scrape(url: str, email: str, password: str, output_dir: Path, no_login: bool = False):
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    course_path = parsed.path  # e.g. /claude-code-101/469788
    parts = course_path.strip('/').split('/')
    course_slug = parts[0] if parts else 'course'

    platform = detect_platform(url)
    print(f"平台识别: {platform}")
    print(f"课程 slug: {course_slug}")
    print(f"输出目录: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent=(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        )
        page = context.new_page()

        # ── 登录 ──
        if not no_login and email:
            print("\n[1] 登录...")
            if platform == 'skilljar':
                login_skilljar(page, base_url, course_path, email, password)
            else:
                goto(page, url)
                # 查找登录链接
                login_link = page.evaluate("""() => {
                    for (const a of document.querySelectorAll('a[href]')) {
                        const t = a.innerText.toLowerCase();
                        const h = a.getAttribute('href') || '';
                        if (t.includes('sign in') || t.includes('log in') ||
                            h.includes('login') || h.includes('sign_in')) {
                            return a.getAttribute('href');
                        }
                    }
                    return null;
                }""")
                if login_link:
                    login_url = login_link if login_link.startswith('http') else f"{base_url}{login_link}"
                    goto(page, login_url)
                if not login_generic(page, email, password):
                    print("  警告：未找到登录表单，继续尝试直接访问...")
        else:
            print("\n[1] 跳过登录，直接访问...")

        # ── 进入课程 ──
        print(f"\n[2] 访问课程页面...")
        goto(page, url)
        print(f"  当前 URL: {page.url}")

        # ── 收集课时链接 ──
        print(f"\n[3] 收集课时链接...")
        if platform == 'skilljar':
            lessons = collect_lesson_links(page, course_slug, base_url)
        else:
            lessons = collect_generic_lesson_links(page, base_url)

        print(f"  找到 {len(lessons)} 个课时链接:")
        for l in lessons:
            print(f"    {l['title']}: {l['url']}")

        # ── 抓取课时内容 ──
        print(f"\n[4] 抓取课时内容...")
        all_lessons = []
        visited = set()

        urls_to_visit = [l['url'] for l in lessons] if lessons else [url]

        for i, lesson_url in enumerate(urls_to_visit):
            if lesson_url in visited:
                continue
            visited.add(lesson_url)

            sidebar_title = next(
                (l['title'] for l in lessons if l['url'] == lesson_url), ""
            )
            print(f"  [{i+1}/{len(urls_to_visit)}] {lesson_url}")
            goto(page, lesson_url)
            hydrate_lazy_content(page)

            title = get_lesson_title(page, sidebar_title)
            extracted = extract_content(page)
            content = extracted.get('markdown', '') if isinstance(extracted, dict) else extracted[0]
            root_selector = extracted.get('selector', '') if isinstance(extracted, dict) else extracted[1]
            page_slug = f"{i+1:02d}-{slugify(title)}"
            images, image_candidates = download_images(context, page, output_dir, page_slug, root_selector=root_selector)
            content = append_image_gallery(localize_markdown_images(content, images), images)
            print(f"    标题: {title} | 内容: {len(content)} 字符 | 图片: {len(images)}/{image_candidates}")

            all_lessons.append({
                'url': lesson_url, 'title': title, 'content': content,
                'images': len(images), 'image_candidates': image_candidates
            })

        # ── Next 按钮补漏 ──
        if all_lessons and platform == 'skilljar':
            print(f"\n[4b] 用 Next 按钮补全遗漏课时...")
            goto(page, urls_to_visit[0])
            max_steps, steps = 30, 0
            while steps < max_steps:
                next_url = get_next_url(page, course_slug, base_url)
                if not next_url or next_url in visited:
                    break
                visited.add(next_url)
                steps += 1
                goto(page, next_url)
                hydrate_lazy_content(page)
                title = get_lesson_title(page)
                extracted = extract_content(page)
                content = extracted.get('markdown', '') if isinstance(extracted, dict) else extracted[0]
                root_selector = extracted.get('selector', '') if isinstance(extracted, dict) else extracted[1]
                page_slug = f"{len(all_lessons)+1:02d}-{slugify(title)}"
                images, image_candidates = download_images(context, page, output_dir, page_slug, root_selector=root_selector)
                content = append_image_gallery(localize_markdown_images(content, images), images)
                if content:
                    print(f"    补漏: {title} ({len(content)} 字符, 图片 {len(images)}/{image_candidates})")
                    all_lessons.append({
                        'url': next_url, 'title': title, 'content': content,
                        'images': len(images), 'image_candidates': image_candidates
                    })

        browser.close()

    # ── 保存文件 ──
    print(f"\n[5] 保存 {len(all_lessons)} 个课时文件...")

    # 索引
    index_lines = [
        f"# {course_slug} 课程内容\n\n",
        f"来源：{url}\n",
        f"抓取日期：{__import__('datetime').date.today()}\n\n",
        "## 目录\n\n"
    ]

    for i, lesson in enumerate(all_lessons):
        fname = f"{i+1:02d}-{slugify(lesson['title'])}.md"
        index_lines.append(f"{i+1}. [{lesson['title']}]({fname})\n")

    with open(output_dir / "00-index.md", 'w', encoding='utf-8') as f:
        f.writelines(index_lines)
    print(f"  保存: 00-index.md")

    for i, lesson in enumerate(all_lessons):
        fname = f"{i+1:02d}-{slugify(lesson['title'])}.md"
        with open(output_dir / fname, 'w', encoding='utf-8') as f:
            f.write(f"# {lesson['title']}\n\n")
            f.write(f"来源：{lesson['url']}\n\n")
            f.write(f"图片 / Images：{lesson.get('images', 0)}/{lesson.get('image_candidates', 0)}\n\n")
            f.write("---\n\n")
            f.write(lesson['content'])
        print(f"  保存: {fname} ({len(lesson['content'])} 字符, 图片 {lesson.get('images', 0)}/{lesson.get('image_candidates', 0)})")

    print(f"\n完成！共 {len(all_lessons)} 个课时 → {output_dir}")
    return all_lessons


# ── 入口 ──────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Course Scraper')
    parser.add_argument('--url', required=True, help='课程 URL（第一个课时或课程首页）')
    parser.add_argument('--email', default='', help='登录邮箱')
    parser.add_argument('--password', default='', help='登录密码')
    parser.add_argument('--output', required=True, help='输出目录（绝对路径）')
    parser.add_argument('--no-login', action='store_true', help='跳过登录')
    args = parser.parse_args()

    scrape(
        url=args.url,
        email=args.email,
        password=args.password,
        output_dir=Path(args.output),
        no_login=args.no_login,
    )
