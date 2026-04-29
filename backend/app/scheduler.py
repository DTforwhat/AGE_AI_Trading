"""APScheduler that runs background data fetches."""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.analysis.hotspot import analyze_hotspots
from app.config import settings
from app.sources.aggregator import (
    aggregate_news,
    refresh_earnings,
    refresh_watchlist_snapshots,
)

logger = logging.getLogger(__name__)


def build_scheduler() -> BackgroundScheduler:
    sched = BackgroundScheduler(timezone="UTC")

    sched.add_job(
        aggregate_news,
        "interval",
        minutes=settings.news_fetch_minutes,
        id="news",
        next_run_time=_now_plus_seconds(5),
        max_instances=1,
    )
    sched.add_job(
        refresh_watchlist_snapshots,
        "interval",
        minutes=settings.price_fetch_minutes,
        id="prices",
        next_run_time=_now_plus_seconds(15),
        max_instances=1,
    )
    sched.add_job(
        analyze_hotspots,
        "interval",
        minutes=settings.hotspot_analysis_minutes,
        id="hotspots",
        next_run_time=_now_plus_seconds(120),  # let news arrive first
        max_instances=1,
    )
    sched.add_job(
        refresh_earnings,
        "interval",
        hours=12,
        id="earnings",
        next_run_time=_now_plus_seconds(60),
        max_instances=1,
    )
    return sched


def _now_plus_seconds(s: int):
    from datetime import datetime, timedelta

    return datetime.utcnow() + timedelta(seconds=s)
