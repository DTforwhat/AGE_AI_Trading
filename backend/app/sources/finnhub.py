"""Finnhub free-tier wrapper. 60 calls/minute limit on the free plan."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BASE = "https://finnhub.io/api/v1"


def _client() -> httpx.Client | None:
    if not settings.finnhub_api_key:
        return None
    return httpx.Client(timeout=10.0, params={"token": settings.finnhub_api_key})


def fetch_general_news() -> list[dict]:
    """General market news, Finnhub-curated."""
    client = _client()
    if not client:
        return []
    try:
        resp = client.get(f"{BASE}/news", params={"category": "general"})
        resp.raise_for_status()
        items = resp.json()
        return [
            {
                "source": f"Finnhub:{it.get('source', 'unknown')}",
                "title": it.get("headline", ""),
                "url": it.get("url", ""),
                "summary": it.get("summary", "")[:600],
                "published_at": datetime.fromtimestamp(it.get("datetime", 0) or 0),
                "tickers": ",".join(it.get("related", "").split(",")) if it.get("related") else "",
            }
            for it in items
            if it.get("url") and it.get("headline")
        ]
    except httpx.HTTPError as exc:
        logger.warning("Finnhub general news failed: %s", exc)
        return []
    finally:
        client.close()


def fetch_company_news(symbol: str, days: int = 7) -> list[dict]:
    """Per-company news for a ticker."""
    client = _client()
    if not client:
        return []
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    try:
        resp = client.get(
            f"{BASE}/company-news",
            params={"symbol": symbol, "from": start.isoformat(), "to": end.isoformat()},
        )
        resp.raise_for_status()
        items = resp.json()
        return [
            {
                "source": f"Finnhub:{it.get('source', 'unknown')}",
                "title": it.get("headline", ""),
                "url": it.get("url", ""),
                "summary": it.get("summary", "")[:600],
                "published_at": datetime.fromtimestamp(it.get("datetime", 0) or 0),
                "tickers": symbol,
            }
            for it in items
            if it.get("url") and it.get("headline")
        ]
    except httpx.HTTPError as exc:
        logger.warning("Finnhub company news failed for %s: %s", symbol, exc)
        return []
    finally:
        client.close()


def fetch_earnings_calendar(days_ahead: int = 14) -> list[dict]:
    """Upcoming earnings reports."""
    client = _client()
    if not client:
        return []
    end = datetime.utcnow().date() + timedelta(days=days_ahead)
    start = datetime.utcnow().date()
    try:
        resp = client.get(
            f"{BASE}/calendar/earnings",
            params={"from": start.isoformat(), "to": end.isoformat()},
        )
        resp.raise_for_status()
        return resp.json().get("earningsCalendar", [])
    except httpx.HTTPError as exc:
        logger.warning("Finnhub earnings calendar failed: %s", exc)
        return []
    finally:
        client.close()
