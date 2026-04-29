from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from app.analysis.trends import trend_signal
from app.config import settings
from app.db import engine
from app.models import EarningsEvent, NewsArticle, StockSnapshot
from app.sources import edgar, yfinance_src

router = APIRouter(prefix="/stocks", tags=["stocks"])


def _latest_snapshot(sess: Session, symbol: str) -> StockSnapshot | None:
    stmt = (
        select(StockSnapshot)
        .where(StockSnapshot.symbol == symbol)
        .order_by(StockSnapshot.fetched_at.desc())
        .limit(1)
    )
    return sess.exec(stmt).first()


@router.get("/watchlist")
def list_watchlist():
    """Return the latest snapshot for each watchlist ticker."""
    out = []
    with Session(engine) as sess:
        for sym in settings.watchlist_tickers:
            snap = _latest_snapshot(sess, sym)
            if not snap:
                # On-the-fly fetch if we haven't snapshot yet
                live = yfinance_src.fetch_snapshot(sym)
                if not live:
                    continue
                out.append({**live, "trend": trend_signal(live)})
                continue
            data = {
                "symbol": snap.symbol,
                "price": snap.price,
                "change_pct": snap.change_pct,
                "volume": snap.volume,
                "market_cap": snap.market_cap,
                "pe_ratio": snap.pe_ratio,
                "fifty_two_week_high": snap.fifty_two_week_high,
                "fifty_two_week_low": snap.fifty_two_week_low,
                "rsi_14": snap.rsi_14,
                "sma_20": snap.sma_20,
                "sma_50": snap.sma_50,
                "sma_200": snap.sma_200,
                "fetched_at": snap.fetched_at.isoformat(),
            }
            out.append({**data, "trend": trend_signal(data)})
    return out


@router.get("/{symbol}")
def stock_detail(symbol: str):
    sym = symbol.upper()
    profile = yfinance_src.fetch_company_profile(sym)
    snapshot = yfinance_src.fetch_snapshot(sym)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No data for {sym}")
    history = yfinance_src.fetch_history(sym, "6mo")

    cutoff = datetime.utcnow() - timedelta(days=14)
    with Session(engine) as sess:
        news_stmt = (
            select(NewsArticle)
            .where(NewsArticle.tickers.contains(sym))
            .where(NewsArticle.published_at >= cutoff)
            .order_by(NewsArticle.published_at.desc())
            .limit(20)
        )
        news = [
            {
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "published_at": a.published_at.isoformat(),
            }
            for a in sess.exec(news_stmt)
        ]
        earnings_stmt = (
            select(EarningsEvent)
            .where(EarningsEvent.symbol == sym)
            .order_by(EarningsEvent.report_date.desc())
            .limit(8)
        )
        earnings = [
            {
                "report_date": e.report_date.isoformat(),
                "eps_estimate": e.eps_estimate,
                "eps_actual": e.eps_actual,
            }
            for e in sess.exec(earnings_stmt)
        ]

    filings = edgar.fetch_recent_filings(sym, ("13F-HR", "4", "8-K", "10-Q", "10-K"))

    return {
        "profile": profile,
        "snapshot": snapshot,
        "trend": trend_signal(snapshot),
        "history": history,
        "news": news,
        "earnings": earnings,
        "filings": filings,
    }


@router.get("/{symbol}/filings")
def stock_filings(symbol: str, form: str | None = Query(None)):
    forms = (form,) if form else ("13F-HR", "4", "8-K", "10-Q", "10-K")
    return edgar.fetch_recent_filings(symbol.upper(), forms)
