from datetime import datetime, timedelta

from fastapi import APIRouter, Query
from sqlmodel import Session, select

from app.db import engine
from app.models import NewsArticle
from app.sources.aggregator import aggregate_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
def list_news(
    hours: int = Query(24, ge=1, le=168),
    ticker: str | None = None,
    source: str | None = None,
    limit: int = Query(100, ge=1, le=500),
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    with Session(engine) as sess:
        stmt = select(NewsArticle).where(NewsArticle.published_at >= cutoff)
        if ticker:
            stmt = stmt.where(NewsArticle.tickers.contains(ticker.upper()))
        if source:
            stmt = stmt.where(NewsArticle.source == source)
        stmt = stmt.order_by(NewsArticle.published_at.desc()).limit(limit)
        rows = list(sess.exec(stmt))
    return [
        {
            "id": r.id,
            "source": r.source,
            "title": r.title,
            "url": r.url,
            "summary": r.summary,
            "published_at": r.published_at.isoformat(),
            "tickers": [t for t in r.tickers.split(",") if t],
        }
        for r in rows
    ]


@router.post("/refresh")
def refresh_news():
    count = aggregate_news()
    return {"new_articles": count}
