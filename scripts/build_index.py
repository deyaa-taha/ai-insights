#!/usr/bin/env python3
"""Regenerate the README index and feed.xml from article/post frontmatter.

Usage: python scripts/build_index.py
Requires: PyYAML (pip install pyyaml)
"""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/deyaa-taha/ai-insights"
BLOB = f"{REPO_URL}/blob/main"
README = ROOT / "README.md"
FEED = ROOT / "feed.xml"
LANG_LABEL = {"en": "English", "he": "עברית", "ar": "العربية"}
LANG_ORDER = {"en": 0, "he": 1, "ar": 2}
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def read_frontmatter(path: Path) -> dict | None:
    match = FM_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return None
    meta = yaml.safe_load(match.group(1)) or {}
    if meta.get("draft"):
        return None
    meta["_path"] = path.relative_to(ROOT).as_posix()
    d = meta.get("date")
    meta["date"] = d if isinstance(d, date) else datetime.strptime(str(d), "%Y-%m-%d").date()
    return meta


def collect_articles() -> list[dict]:
    """One entry per article folder, keyed on the English index.md (or the first file found)."""
    articles = []
    for folder in sorted((ROOT / "articles").glob("*/*/")):
        main = folder / "index.md"
        candidates = [main] if main.exists() else sorted(folder.glob("index*.md"))
        if not candidates:
            continue
        meta = read_frontmatter(candidates[0])
        if not meta:
            continue
        langs = {}
        for f in sorted(folder.glob("index*.md")):
            m = read_frontmatter(f)
            if m:
                langs[m.get("lang", "en")] = m["_path"]
        meta["_langs"] = langs
        articles.append(meta)
    return sorted(articles, key=lambda a: a["date"], reverse=True)


def collect_posts() -> list[dict]:
    posts = [m for f in (ROOT / "posts").glob("*/*.md") if (m := read_frontmatter(f))]
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def render_articles(articles: list[dict]) -> str:
    if not articles:
        return "_No articles yet._"
    lines = []
    for a in articles:
        tags = " ".join(f"`{t}`" for t in a.get("tags", []))
        langs = " · ".join(
            f"[{LANG_LABEL.get(code, code)}]({path})"
        for code, path in sorted(a["_langs"].items(), key=lambda kv: LANG_ORDER.get(kv[0], 99))
        )
        lines.append(
            f"- **[{a['title']}]({a['_path']})** · {a['date']:%Y-%m-%d}  \n"
            f"  {a.get('summary', '')}  \n"
            f"  🌐 {langs}  {tags}"
        )
    return "\n".join(lines)


def render_posts(posts: list[dict], limit: int = 10) -> str:
    if not posts:
        return "_No posts yet._"
    return "\n".join(
        f"- [{p['title']}]({p['_path']}) · {p['date']:%Y-%m-%d}" for p in posts[:limit]
    )


def render_tags(items: list[dict]) -> str:
    counts: dict[str, int] = {}
    for item in items:
        for t in item.get("tags", []):
            counts[t] = counts.get(t, 0) + 1
    return " ".join(f"`{t}` ({n})" for t, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def replace_block(text: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"README is missing the {name}:START/END markers")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


def build_feed(items: list[dict]) -> str:
    entries = []
    for it in sorted(items, key=lambda i: i["date"], reverse=True)[:30]:
        dt = datetime.combine(it["date"], datetime.min.time(), tzinfo=timezone.utc)
        link = f"{BLOB}/{it['_path']}"
        entries.append(
            "    <item>\n"
            f"      <title>{escape(it['title'])}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"true\">{link}</guid>\n"
            f"      <pubDate>{format_datetime(dt)}</pubDate>\n"
            f"      <description>{escape(it.get('summary', ''))}</description>\n"
            "    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n  <channel>\n'
        "    <title>AI Insights · Deyaa Taha</title>\n"
        f"    <link>{REPO_URL}</link>\n"
        "    <description>Articles and posts on AI engineering, agents, RAG and enterprise AI adoption.</description>\n"
        + "\n".join(entries)
        + "\n  </channel>\n</rss>\n"
    )


def main() -> None:
    articles, posts = collect_articles(), collect_posts()
    text = README.read_text(encoding="utf-8")
    text = replace_block(text, "ARTICLES", render_articles(articles))
    text = replace_block(text, "POSTS", render_posts(posts))
    text = replace_block(text, "TAGS", render_tags(articles + posts))
    README.write_text(text, encoding="utf-8")
    FEED.write_text(build_feed(articles + posts), encoding="utf-8")
    print(f"Indexed {len(articles)} article(s), {len(posts)} post(s).")


if __name__ == "__main__":
    main()
