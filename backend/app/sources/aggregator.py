"""Aggregate news from all configured sources and persist to DB."""

from __future__ import annotations

import logging

from sqlmodel import Session, select

from app.config import settings
from app.db import engine
from app.models import NewsArticle, StockSnapshot, EarningsEvent
from app.sources import finnhub, newsapi, rss, yfinance_src

logger = logging.getLogger(__name__)


def aggregate_news() -> int:
    """Pull from RSS + Finnhub + NewsAPI, dedupe by URL, save new ones."""
    watchlist = settings.watchlist_tickers

    bundles = [
        rss.fetch_all(watchlist),
        finnhub.fetch_general_news(),
        newsapi.fetch_business_headlines(),
    ]

    seen_urls: set[str] = set()
    new_count = 0
    with Session(engine) as sess:
        existing = {row[0] for row in sess.exec(select(NewsArticle.url)).all()}
        for batch in bundles:
            for art in batch:
                url = art.get("url")
                if not url or url in seen_urls or url in existing:
                    continue
                seen_urls.add(url)
                sess.add(NewsArticle(**art))
                new_count += 1
        sess.commit()
    logger.info("Aggregated %d new articles", new_count)
    return new_count


def refresh_watchlist_snapshots() -> int:
    """Refresh latest price snapshot for every ticker in the watchlist."""
    count = 0
    with Session(engine) as sess:
        for sym in settings.watchlist_tickers:
            snap = yfinance_src.fetch_snapshot(sym)
            if snap:
                sess.add(StockSnapshot(**snap))
                count += 1
        sess.commit()
    logger.info("Refreshed %d watchlist snapshots", count)
    return count


def refresh_earnings() -> int:
    """Pull recent earnings dates from yfinance for the watchlist."""
    count = 0
    with Session(engine) as sess:
        existing = {
            (sym, dt.date())
            for sym, dt in sess.exec(
                select(EarningsEvent.symbol, EarningsEvent.report_date)
            ).all()
        }
        for sym in settings.watchlist_tickers:
            for ev in yfinance_src.fetch_earnings_dates(sym):
                key = (ev["symbol"], ev["report_date"].date())
                if key in existing:
                    continue
                sess.add(EarningsEvent(**ev))
                count += 1
        sess.commit()
    logger.info("Stored %d new earnings events", count)
    return count
