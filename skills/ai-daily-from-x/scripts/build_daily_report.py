#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import time
from email.utils import parsedate_to_datetime
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone, time as dt_time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from account_merge import (
    default_follow_builders_json,
    default_source_md,
    load_extra_handles_from_json,
    merge_handle_lists,
)

X_API_BASE = "https://api.x.com/2"


@dataclass
class Signal:
    handle: str
    text: str
    text_zh: str
    url: str
    published_at: str
    source: str
    relevance: float
    actionable: float
    novelty: float
    impact: float
    timeliness: float
    score: float
    priority: str


TOPIC_HINT_KEYWORDS: dict[str, list[str]] = {
    "agent": ["agent", "agentic", "agents"],
    "mcp": ["mcp"],
    "codex": ["codex"],
    "cursor": ["cursor"],
    "claude": ["claude"],
    "release": ["release", "launch", "shipped", "announced"],
    "open_source": ["open source", "open-source", "mit license"],
    "benchmark": ["benchmark", "sota", "eval"],
    "model": ["model", "llm", "gpt", "opus"],
    "workflow": ["workflow", "fde", "forward deployed"],
}


def http_get_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 8) -> Any:
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get_text(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 8) -> str:
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def http_post_json(
    url: str,
    payload: dict,
    headers: Dict[str, str],
    timeout: int = 90,
) -> Any:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=body, headers=headers, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def text_mostly_chinese(s: str) -> bool:
    """判断是否以中文为主，避免重复翻译。"""
    if not s or not s.strip():
        return True
    cjk = sum(1 for c in s if "\u4e00" <= c <= "\u9fff")
    return cjk / max(len(s), 1) > 0.12


def translate_to_zh_openrouter(
    text: str,
    api_key: str,
    model: str,
    base_url: str,
    http_referer: str,
) -> str:
    """调用 OpenRouter（OpenAI 兼容 chat/completions）英译中。"""
    t = text.strip()
    if not t:
        return ""
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if http_referer:
        headers["HTTP-Referer"] = http_referer
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是专业翻译。将用户给出的社交媒体帖文译为自然流畅的中文。"
                    "保留：@用户名、URL、版本号、产品名、代码片段与英文专有名词（必要时可中英并列）。"
                    "不要添加评论。只输出译文本身。"
                ),
            },
            {"role": "user", "content": t},
        ],
        "temperature": 0.2,
    }
    data = http_post_json(url, payload, headers, timeout=120)
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    out = (msg.get("content") or "").strip()
    return out


def enrich_signals_zh(
    signals: list[Signal],
    api_key: str,
    model: str,
    base_url: str,
    http_referer: str,
    max_chars: int,
    sleep_s: float,
) -> list[Signal]:
    """为每条 Signal 填充 text_zh（去重缓存相同正文）。"""
    if not signals:
        return signals
    cache: dict[str, str] = {}
    out: list[Signal] = []
    for s in signals:
        key = hashlib.sha256(s.text.encode("utf-8")).hexdigest()
        if key in cache:
            out.append(replace(s, text_zh=cache[key]))
            continue
        if text_mostly_chinese(s.text):
            cache[key] = s.text
            out.append(replace(s, text_zh=s.text))
            continue
        if not api_key:
            cache[key] = ""
            out.append(replace(s, text_zh=""))
            continue
        chunk = s.text[:max_chars] if len(s.text) > max_chars else s.text
        try:
            zh = translate_to_zh_openrouter(chunk, api_key, model, base_url, http_referer)
            if len(s.text) > max_chars:
                zh = zh + "\n\n（原文过长，仅翻译前 {0} 字）".format(max_chars)
        except Exception as e:
            print(f"[ai-daily-from-x] 翻译失败 @{s.handle}: {type(e).__name__}: {e}", flush=True)
            zh = ""
        cache[key] = zh
        out.append(replace(s, text_zh=zh))
        if sleep_s > 0:
            time.sleep(sleep_s)
    return out


def extract_handles(markdown_text: str) -> list[str]:
    link_handles = re.findall(r"twitter\.com/([A-Za-z0-9_]{1,15})", markdown_text, flags=re.IGNORECASE)
    plain_handles = re.findall(r"(?<![A-Za-z0-9_])@([A-Za-z0-9_]{1,15})", markdown_text)
    dedup: list[str] = []
    for raw in link_handles + plain_handles:
        handle = raw.strip().lstrip("@")
        if not handle:
            continue
        if handle not in dedup:
            dedup.append(handle)
    return dedup


def load_handles(accounts_file: Path, source_markdown: Path) -> list[str]:
    if accounts_file.exists():
        data = json.loads(accounts_file.read_text(encoding="utf-8"))
        handles = data.get("handles", [])
        if handles:
            return handles
    text = source_markdown.read_text(encoding="utf-8")
    handles = extract_handles(text)
    # 与 parse_accounts 一致：无 accounts.json 时仍合并 follow-builders 扩展名单
    merge_path = default_follow_builders_json()
    if merge_path.exists():
        try:
            extra = load_extra_handles_from_json(merge_path)
            handles = merge_handle_lists(handles, extra)
        except Exception as e:
            print(f"[ai-daily-from-x] 合并 follow-builders 名单失败: {e}", flush=True)
    return handles


def resolve_window(report_date: Optional[str], tz_name: str):
    tz = ZoneInfo(tz_name)
    if report_date:
        day = datetime.strptime(report_date, "%Y-%m-%d").date()
    else:
        day = (datetime.now(tz) - timedelta(days=1)).date()
    start_local = datetime.combine(day, dt_time.min, tzinfo=tz)
    end_local = datetime.combine(day, dt_time.max, tzinfo=tz)
    return day.isoformat(), start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def fetch_user_id_ex(handle: str, bearer: str) -> tuple[Optional[str], Optional[int]]:
    """返回 (user_id, http_error_code)。http_error_code 仅在 HTTPError 时有值。"""
    url = f"{X_API_BASE}/users/by/username/{quote(handle)}"
    headers = {"Authorization": f"Bearer {bearer}"}
    try:
        data = http_get_json(url, headers=headers)
        uid = data.get("data", {}).get("id")
        return uid, None
    except HTTPError as e:
        return None, e.code
    except Exception:
        return None, None


def fetch_tweets_by_user_id(
    handle: str,
    user_id: str,
    bearer: str,
    start_utc: datetime,
    end_utc: datetime,
) -> list[dict[str, str]]:
    params = urlencode(
        {
            "max_results": 20,
            "start_time": start_utc.isoformat().replace("+00:00", "Z"),
            "end_time": end_utc.isoformat().replace("+00:00", "Z"),
            "tweet.fields": "created_at,text,id",
            "exclude": "retweets,replies",
        }
    )
    url = f"{X_API_BASE}/users/{user_id}/tweets?{params}"
    headers = {"Authorization": f"Bearer {bearer}"}
    try:
        data = http_get_json(url, headers=headers)
    except (HTTPError, URLError):
        return []
    tweets = []
    for item in data.get("data", []):
        tid = item.get("id", "")
        tweets.append(
            {
                "text": item.get("text", "").strip(),
                "published_at": item.get("created_at", ""),
                "url": f"https://x.com/{handle}/status/{tid}",
                "source": "x_api",
            }
        )
    return tweets


def nitter_rss_link_to_x(link: str, handle: str) -> str:
    m = re.match(r"https?://[^/]+/([^/]+)/status/(\d+)", link)
    if m:
        return f"https://x.com/{m.group(1)}/status/{m.group(2)}"
    return f"https://x.com/{handle}"


def fetch_tweets_by_nitter_rss(
    handle: str,
    start_utc: datetime,
    end_utc: datetime,
) -> list[dict[str, str]]:
    """通过 Nitter 公开 RSS 拉取时间窗内条目（不依赖 X 付费 API）。host 可用环境变量 NITTER_HOSTS 逗号分隔。"""
    raw_hosts = os.getenv("NITTER_HOSTS", "nitter.net")
    hosts = [h.strip() for h in raw_hosts.split(",") if h.strip()]
    for host in hosts:
        rss_url = f"https://{host}/{quote(handle)}/rss"
        try:
            xml = http_get_text(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        except Exception:
            continue
        items_out: list[dict[str, str]] = []
        for block in re.split(r"<item>", xml)[1:]:
            part = block.split("</item>", 1)[0]
            link_m = re.search(r"<link>([^<]+)</link>", part)
            pub_m = re.search(r"<pubDate>([^<]+)</pubDate>", part)
            title_m = re.search(r"<title>(.*?)</title>", part, re.DOTALL)
            if not link_m or not pub_m:
                continue
            link = link_m.group(1).strip()
            try:
                pub = parsedate_to_datetime(pub_m.group(1).strip())
                if pub.tzinfo is None:
                    pub = pub.replace(tzinfo=timezone.utc)
            except Exception:
                continue
            if not (start_utc <= pub <= end_utc):
                continue
            title = title_m.group(1).strip() if title_m else ""
            title = re.sub(r"\s+", " ", title)
            items_out.append(
                {
                    "text": title or f"@{handle} 动态",
                    "published_at": pub.isoformat().replace("+00:00", "Z"),
                    "url": nitter_rss_link_to_x(link, handle),
                    "source": "nitter_rss",
                }
            )
        return items_out
    return []


def fetch_tweets_by_websearch(handle: str, date_iso: str) -> list[dict[str, str]]:
    # 使用公开搜索回退，规避 API 失败场景。
    query = f"site:x.com/{handle}/status {date_iso} AI coding"
    url = f"https://duckduckgo.com/html/?q={quote(query)}"
    try:
        html = http_get_text(url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception:
        return []
    raw_links = re.findall(r'href="([^"]+)"', html)
    links: list[str] = []
    for raw in raw_links:
        # DuckDuckGo 常返回 /l/?uddg=<encoded_url>，这里解码真实跳转链接。
        if raw.startswith("/l/?"):
            query = urlparse(raw).query
            params = parse_qs(query)
            uddg = params.get("uddg", [])
            if uddg:
                raw = unquote(uddg[0])
        if raw.startswith("//"):
            raw = "https:" + raw
        if re.search(r"https?://(x|twitter)\.com/[^/]+/status/\d+", raw):
            links.append(raw)
    snippets = re.findall(r'class="result__snippet".*?>(.*?)</a>', html)
    cleaned: list[dict[str, str]] = []
    for idx, link in enumerate(links[:8]):
        snippet = re.sub("<.*?>", "", snippets[idx] if idx < len(snippets) else "").strip()
        cleaned.append(
            {
                "text": snippet or f"{handle} 昨日动态（Web 搜索回退）",
                "published_at": f"{date_iso}T12:00:00Z",
                "url": link.replace("&amp;", "&"),
                "source": "websearch_fallback",
            }
        )
    return cleaned


def score_text(text: str) -> tuple[float, float, float, float, float]:
    t = text.lower()
    relevance_words = ["agent", "model", "code", "coding", "cursor", "mcp", "api", "release", "benchmark"]
    actionable_words = ["how", "guide", "open source", "repo", "demo", "tutorial", "best practice"]
    novelty_words = ["new", "launch", "released", "v2", "breakthrough", "sota", "announce"]
    impact_words = ["openai", "anthropic", "google", "meta", "nvidia", "deepmind", "copilot", "cursor"]
    relevance = min(10.0, 4.0 + sum(1 for w in relevance_words if w in t) * 0.8)
    actionable = min(10.0, 4.0 + sum(1 for w in actionable_words if w in t) * 1.1)
    novelty = min(10.0, 3.5 + sum(1 for w in novelty_words if w in t) * 1.2)
    impact = min(10.0, 4.0 + sum(1 for w in impact_words if w in t) * 1.0)
    timeliness = 8.5
    return relevance, actionable, novelty, impact, timeliness


def text_preview(text: str, max_len: int = 120) -> str:
    t = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    if len(t) > max_len:
        return t[: max_len - 1] + "…"
    return t


def topic_hints(text: str) -> list[str]:
    t = text.lower()
    hints: list[str] = []
    for label, words in TOPIC_HINT_KEYWORDS.items():
        if any(w in t for w in words):
            hints.append(label)
    return hints


def compute_priority(score: float) -> str:
    if score >= 9.0:
        return "P0"
    if score >= 8.0:
        return "P1"
    return "P2"


def to_signal(handle: str, item: dict[str, str]) -> Signal:
    relevance, actionable, novelty, impact, timeliness = score_text(item["text"])
    score = relevance * 0.3 + actionable * 0.25 + novelty * 0.2 + impact * 0.2 + timeliness * 0.05
    score = round(score, 2)
    return Signal(
        handle=handle,
        text=item["text"],
        text_zh=item.get("text_zh") or "",
        url=item["url"],
        published_at=item["published_at"],
        source=item["source"],
        relevance=round(relevance, 2),
        actionable=round(actionable, 2),
        novelty=round(novelty, 2),
        impact=round(impact, 2),
        timeliness=round(timeliness, 2),
        score=score,
        priority=compute_priority(score),
    )


def signal_to_candidate_dict(s: Signal) -> dict[str, Any]:
    d = asdict(s)
    d["text_preview"] = text_preview(s.text)
    d["topic_hints"] = topic_hints(s.text)
    return d


def build_observation_top_n(signals: list[Signal], n: int = 15) -> list[dict[str, Any]]:
    top = sorted(signals, key=lambda x: x.score, reverse=True)[:n]
    return [
        {
            "handle": s.handle,
            "score": s.score,
            "priority": s.priority,
            "url": s.url,
            "text_preview": text_preview(s.text),
            "topic_hints": topic_hints(s.text),
        }
        for s in top
    ]


def md_table_cell(text: str, max_len: int = 72) -> str:
    """表格单元格内安全截断，避免竖线破坏表格。"""
    t = text.replace("\n", " ").replace("|", "｜").strip()
    if len(t) > max_len:
        t = t[: max_len - 1] + "…"
    return t


def deduplicate(signals: list[Signal]) -> list[Signal]:
    seen: set[str] = set()
    result: list[Signal] = []
    for s in sorted(signals, key=lambda x: x.score, reverse=True):
        key = re.sub(r"\s+", " ", s.text.lower())[:100]
        if key in seen:
            continue
        seen.add(key)
        result.append(s)
    return result


def render_draft_markdown(
    day: str,
    day_compact: str,
    start_utc: datetime,
    end_utc: datetime,
    selected: list[Signal],
    stats: dict[str, Any],
    deduped: list[Signal],
    min_score: float,
    top_n: int,
    index_limit: int = 30,
) -> str:
    """阶段 1 草稿 MD：统计 + 候选索引；可读定稿由 ai-daily-from-x 技能（阶段 2）覆盖本文件。"""
    lines: list[str] = []
    lines.append(f"# AI 日报草稿（{day}）")
    lines.append("")
    lines.append(
        "> 本文件为采集草稿。请在 Cursor **激活 ai-daily-from-x 技能**（默认会读"
        f"`daily_{day_compact}.raw.json` 并覆盖本文件为可读定稿）。"
    )
    lines.append("")
    lines.append("## 采集摘要")
    lines.append("")
    lines.append(f"- 统计窗口（UTC）：`{start_utc.isoformat()}` ~ `{end_utc.isoformat()}`")
    lines.append(f"- 覆盖账号数：`{stats['handles_total']}`")
    lines.append(f"- API 命中：`{stats['api_hits']}`")
    lines.append(f"- Nitter RSS 命中：`{stats.get('nitter_hits', 0)}`")
    lines.append(f"- Web 搜索回退命中：`{stats['fallback_hits']}`")
    if stats.get("api_abort_reason"):
        lines.append(f"- API 提前结束：`{stats['api_abort_reason']}`")
    tr = stats.get("translation") or {}
    if tr:
        cfg = "已配置 `OPENROUTER_API_KEY`" if tr.get("api_configured") else "未配置（`text_zh` 为空）"
        lines.append(f"- 译文：{cfg}；`text_zh` 非空：`{tr.get('text_zh_non_empty', 0)}` / `{len(deduped)}`")
    eligible = [s for s in deduped if s.score >= min_score]
    lines.append(f"- 去重候选：`{len(deduped)}`；达线（≥ `{min_score}`）：`{len(eligible)}`；脚本入选：`{len(selected)}`")
    lines.append(f"- 事实包：`output/ai-daily-from-x/daily_{day_compact}.raw.json`")
    lines.append("")
    lines.append("## 候选索引（按分数降序）")
    lines.append("")
    lines.append("| 分数 | 账号 | 主题 | 预览 | 链接 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for s in sorted(deduped, key=lambda x: x.score, reverse=True)[:index_limit]:
        hints = ", ".join(topic_hints(s.text)) or "—"
        lines.append(
            f"| {s.score} | @{s.handle} | {md_table_cell(hints, 24)} | "
            f"{md_table_cell(text_preview(s.text), 48)} | {s.url} |"
        )
    if len(deduped) > index_limit:
        lines.append("")
        lines.append(f"> 另有 `{len(deduped) - index_limit}` 条见 raw JSON 的 `all_candidates`。")
    lines.append("")
    lines.append("## 下一步（ai-daily-from-x 技能定稿）")
    lines.append("")
    lines.append("在 Cursor **激活 ai-daily-from-x 技能**（或说「生成 AI 日报」），将自动读 raw 并覆盖本文件。")
    lines.append("")
    lines.append("仅补跑定稿时可以说：")
    lines.append("")
    lines.append(
        f"```\n根据 output/ai-daily-from-x/daily_{day_compact}.raw.json 写今日可读 AI 日报，覆盖 daily_{day_compact}.md\n```"
    )
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 AI 日报")
    parser.add_argument("--accounts", default="output/ai-daily-from-x/accounts.json")
    parser.add_argument(
        "--source-md",
        default=None,
        help="主名单 Markdown（不传则用 skill 内置 assets/ai-influencers-list.md）",
    )
    parser.add_argument("--output-dir", default="output/ai-daily-from-x")
    parser.add_argument("--report-date", default=os.getenv("REPORT_DATE"))
    parser.add_argument("--tz", default=os.getenv("REPORT_TZ", "Asia/Shanghai"))
    parser.add_argument("--top-n", type=int, default=int(os.getenv("TOP_N", "20")))
    parser.add_argument("--min-score", type=float, default=float(os.getenv("MIN_SCORE", "6.0")))
    parser.add_argument("--max-fallback-handles", type=int, default=int(os.getenv("MAX_FALLBACK_HANDLES", "12")))
    parser.add_argument(
        "--md-appendix-limit",
        type=int,
        default=int(os.getenv("MD_APPENDIX_LIMIT", "40")),
        help="MD 附录表格最多行数（未达分数线 / 被 top_n 截断）",
    )
    parser.add_argument(
        "--skip-translate",
        action="store_true",
        help="跳过英译中（不调用 OpenRouter，text_zh 留空）",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    day, start_utc, end_utc = resolve_window(args.report_date, args.tz)
    source_md = Path(args.source_md).expanduser() if args.source_md else default_source_md()
    handles = load_handles(Path(args.accounts), source_md)
    bearer = os.getenv("X_BEARER_TOKEN", "").strip()

    all_signals: list[Signal] = []
    stats: dict[str, Any] = {
        "handles_total": len(handles),
        "api_hits": 0,
        "nitter_hits": 0,
        "fallback_hits": 0,
        "api_fail_handles": [],
        "api_abort_reason": None,
    }

    api_skip_rest = False
    fallback_used_handles = 0
    for handle in handles:
        api_items: list[dict[str, str]] = []
        if bearer and not api_skip_rest:
            try:
                user_id, err_code = fetch_user_id_ex(handle, bearer)
                if err_code in (401, 402):
                    api_skip_rest = True
                    stats["api_abort_reason"] = f"http_{err_code}"
                elif user_id:
                    api_items = fetch_tweets_by_user_id(handle, user_id, bearer, start_utc, end_utc)
            except Exception:
                api_items = []
        if api_items:
            stats["api_hits"] += len(api_items)
            for item in api_items:
                all_signals.append(to_signal(handle, item))
            continue

        if bearer:
            stats["api_fail_handles"].append(handle)

        nitter_items = fetch_tweets_by_nitter_rss(handle, start_utc, end_utc)
        stats["nitter_hits"] += len(nitter_items)
        if nitter_items:
            for item in nitter_items:
                all_signals.append(to_signal(handle, item))
            continue

        if fallback_used_handles >= args.max_fallback_handles:
            continue
        fallback_items = fetch_tweets_by_websearch(handle, day)
        fallback_used_handles += 1
        stats["fallback_hits"] += len(fallback_items)
        for item in fallback_items:
            all_signals.append(to_signal(handle, item))

    deduped = deduplicate(all_signals)

    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if args.skip_translate or os.getenv("SKIP_TRANSLATE", "").strip().lower() in ("1", "true", "yes"):
        openrouter_key = ""
    translate_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()
    translate_base = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
    translate_referer = os.getenv("OPENROUTER_HTTP_REFERER", os.getenv("SITE_URL", "")).strip()
    translate_max_chars = int(os.getenv("TRANSLATE_MAX_CHARS", "8000"))
    translate_sleep = float(os.getenv("TRANSLATE_SLEEP_SEC", "0.15"))

    deduped = enrich_signals_zh(
        deduped,
        openrouter_key,
        translate_model,
        translate_base,
        translate_referer,
        translate_max_chars,
        translate_sleep,
    )
    stats["translation"] = {
        "api_configured": bool(openrouter_key),
        "model": translate_model if openrouter_key else None,
        "text_zh_non_empty": sum(1 for s in deduped if (s.text_zh or "").strip()),
    }

    selected = [s for s in deduped if s.score >= args.min_score][: args.top_n]
    observation_n = int(os.getenv("OBSERVATION_TOP_N", "15"))
    observation_top_n = build_observation_top_n(deduped, observation_n)

    day_compact = day.replace("-", "")
    raw_path = output_dir / f"daily_{day_compact}.raw.json"
    md_path = output_dir / f"daily_{day_compact}.md"

    raw_payload: dict[str, Any] = {
        "schema": "ai-daily-from-x-raw-v1",
        "date": day,
        "window_utc": {
            "start": start_utc.isoformat(),
            "end": end_utc.isoformat(),
        },
        "params": {
            "top_n": args.top_n,
            "min_score": args.min_score,
            "timezone": args.tz,
        },
        "stats": stats,
        "selected": [signal_to_candidate_dict(s) for s in selected],
        "observation_top_n": observation_top_n,
        "all_candidates": [signal_to_candidate_dict(s) for s in deduped],
        "compose_hint": (
            f"在 Cursor 激活 ai-daily-from-x 技能，读取本文件并覆盖 daily_{day_compact}.md（见 SKILL.md 阶段 2）"
        ),
    }
    raw_path.write_text(
        json.dumps(raw_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_path.write_text(
        render_draft_markdown(
            day,
            day_compact,
            start_utc,
            end_utc,
            selected,
            stats,
            deduped,
            args.min_score,
            args.top_n,
        ),
        encoding="utf-8",
    )
    print(f"事实包已生成: {raw_path}")
    print(f"草稿 MD 已生成: {md_path}")
    print("可读定稿：在 Cursor 激活 ai-daily-from-x 技能（见草稿 MD 底部提示）")


if __name__ == "__main__":
    main()
