"""NewsAPI free-tier (100 req/day, last-24h news only on free plan)."""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def fetch_business_headlines() -> list[dict]:
    if not settings.newsapi_key:
        return []
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "category": "business",
                    "language": "en",
                    "pageSize": 50,
                    "apiKey": settings.newsapi_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "source": f"NewsAPI:{a.get('source', {}).get('name', 'unknown')}",
                    "title": a.get("title", "") or "",
                    "url": a.get("url", "") or "",
                    "summary": (a.get("description") or "")[:600],
                    "published_at": _parse_dt(a.get("publishedAt")),
                    "tickers": "",
                }
                for a in data.get("articles", [])
                if a.get("url") and a.get("title")
            ]
    except httpx.HTTPError as exc:
        logger.warning("NewsAPI fetch failed: %s", exc)
        return []


def _parse_dt(s: str | None) -> datetime:
    if not s:
        return datetime.utcnow()
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return datetime.utcnow()
