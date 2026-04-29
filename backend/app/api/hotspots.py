from fastapi import APIRouter, Query
from sqlmodel import Session, select

from app.analysis.hotspot import analyze_hotspots
from app.db import engine
from app.models import Hotspot

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.get("")
def list_hotspots(limit: int = Query(20, ge=1, le=100)):
    with Session(engine) as sess:
        stmt = select(Hotspot).order_by(Hotspot.created_at.desc()).limit(limit)
        rows = list(sess.exec(stmt))
    return [
        {
            "id": r.id,
            "title": r.title,
            "summary": r.summary,
            "tickers": [t for t in r.tickers.split(",") if t],
            "sentiment": r.sentiment,
            "article_count": r.article_count,
            "article_urls": [u for u in r.article_urls.split("\n") if u],
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.post("/refresh")
def refresh_hotspots(hours: int = Query(12, ge=1, le=72)):
    out = analyze_hotspots(hours=hours)
    return {"created": len(out), "hotspots": out}
