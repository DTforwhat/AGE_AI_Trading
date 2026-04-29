from datetime import datetime, timedelta

from fastapi import APIRouter
from sqlmodel import Session, func, select

from app.config import settings
from app.db import engine
from app.models import EarningsEvent, Hotspot, NewsArticle, StockSnapshot

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard_summary():
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)
    cutoff_7d = datetime.utcnow() - timedelta(days=7)
    cutoff_earnings = datetime.utcnow()

    with Session(engine) as sess:
        articles_24h = sess.exec(
            select(func.count(NewsArticle.id)).where(NewsArticle.published_at >= cutoff_24h)
        ).one()
        recent_hotspots = list(
            sess.exec(
                select(Hotspot)
                .where(Hotspot.created_at >= cutoff_7d)
                .order_by(Hotspot.created_at.desc())
                .limit(5)
            )
        )
        upcoming_earnings = list(
            sess.exec(
                select(EarningsEvent)
                .where(EarningsEvent.report_date >= cutoff_earnings)
                .order_by(EarningsEvent.report_date.asc())
                .limit(10)
            )
        )

        # Top movers from latest snapshot per symbol
        snapshots = []
        for sym in settings.watchlist_tickers:
            snap = sess.exec(
                select(StockSnapshot)
                .where(StockSnapshot.symbol == sym)
                .order_by(StockSnapshot.fetched_at.desc())
                .limit(1)
            ).first()
            if snap:
                snapshots.append(snap)

    snapshots.sort(key=lambda s: abs(s.change_pct or 0), reverse=True)
    top_movers = [
        {"symbol": s.symbol, "price": s.price, "change_pct": s.change_pct}
        for s in snapshots[:8]
    ]

    return {
        "articles_24h": articles_24h,
        "watchlist_size": len(settings.watchlist_tickers),
        "top_movers": top_movers,
        "recent_hotspots": [
            {
                "id": h.id,
                "title": h.title,
                "summary": h.summary,
                "tickers": [t for t in h.tickers.split(",") if t],
                "sentiment": h.sentiment,
                "created_at": h.created_at.isoformat(),
            }
            for h in recent_hotspots
        ],
        "upcoming_earnings": [
            {
                "symbol": e.symbol,
                "report_date": e.report_date.isoformat(),
                "eps_estimate": e.eps_estimate,
            }
            for e in upcoming_earnings
        ],
    }
