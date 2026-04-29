"""Aggregate financial RSS feeds (no API key needed)."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Iterable

import feedparser

logger = logging.getLogger(__name__)

# Curated list of free financial RSS feeds. All publicly accessible.
RSS_FEEDS: list[tuple[str, str]] = [
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    ("CNBC Top News", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("CNBC Markets", "https://www.cnbc.com/id/15839069/device/rss/rss.html"),
    ("MarketWatch Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
    ("MarketWatch Real-time", "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines"),
    ("Seeking Alpha Market News", "https://seekingalpha.com/market_currents.xml"),
    ("Reuters Business", "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"),
    ("Investing.com News", "https://www.investing.com/rss/news.rss"),
    ("FT Companies", "https://www.ft.com/companies?format=rss"),
    ("WSJ Markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
]

TICKER_RE = re.compile(r"\b[A-Z]{1,5}\b")


def extract_tickers(text: str, watchlist: Iterable[str]) -> list[str]:
    """Find tickers from a watchlist that appear in text."""
    found = set()
    upper = text.upper()
    for sym in watchlist:
        # Match either the bare symbol or $SYM convention
        if re.search(rf"(?:^|[^A-Z]){re.escape(sym)}(?:[^A-Z]|$)", upper):
            found.add(sym)
    return sorted(found)


def parse_published(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None) or entry.get(key)
        if val:
            try:
                return datetime(*val[:6])
            except (TypeError, ValueError):
                continue
    return datetime.utcnow()


def fetch_all(watchlist: list[str]) -> list[dict]:
    """Fetch all RSS feeds and return normalized article dicts."""
    articles: list[dict] = []
    for name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:30]:
                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()
                if not title or not link:
                    continue
                summary = (entry.get("summary") or entry.get("description") or "").strip()
                # Strip HTML tags from summary
                summary = re.sub(r"<[^>]+>", "", summary)[:600]
                tickers = extract_tickers(f"{title} {summary}", watchlist)
                articles.append(
                    {
                        "source": name,
                        "title": title,
                        "url": link,
                        "summary": summary,
                        "published_at": parse_published(entry),
                        "tickers": ",".join(tickers),
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("RSS fetch failed for %s: %s", name, exc)
    return articles
