"""Claude-powered hotspot clustering and analysis.

Takes the last N news articles, sends them to Claude Haiku 4.5 with prompt
caching on the system prompt, and asks for clustered hotspots in JSON form.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any

import anthropic
from sqlmodel import Session, select

from app.config import settings
from app.db import engine
from app.models import Hotspot, NewsArticle

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """You are a financial markets analyst. You receive a batch of recent
financial news headlines (with optional summaries) and must group them into the
2-6 most important market hotspots right now.

For each hotspot return:
- title: short headline-style topic name (under 80 chars)
- summary: 2-3 sentences explaining what's happening and why it matters
- tickers: array of ticker symbols most affected (e.g. ["NVDA","AMD"]). Empty array if macro.
- sentiment: one of "bullish", "bearish", "neutral"
- article_indexes: array of 0-based indexes of the input articles that belong to this cluster

Skip lifestyle, sports, weather, generic political news with no market impact.
Return ONLY valid JSON matching the schema. No prose, no markdown."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "hotspots": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "tickers": {"type": "array", "items": {"type": "string"}},
                    "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                    "article_indexes": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["title", "summary", "tickers", "sentiment", "article_indexes"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["hotspots"],
    "additionalProperties": False,
}


def _format_articles(articles: list[NewsArticle]) -> str:
    lines = []
    for i, a in enumerate(articles):
        ts = a.published_at.strftime("%Y-%m-%d %H:%M")
        line = f"[{i}] ({ts}) [{a.source}] {a.title}"
        if a.summary:
            line += f"\n    {a.summary[:240]}"
        if a.tickers:
            line += f"\n    tickers: {a.tickers}"
        lines.append(line)
    return "\n".join(lines)


def analyze_hotspots(hours: int = 12, max_articles: int = 80) -> list[dict[str, Any]]:
    """Pull recent articles, send to Claude, store and return hotspot clusters."""
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set; skipping hotspot analysis")
        return []

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    with Session(engine) as sess:
        stmt = (
            select(NewsArticle)
            .where(NewsArticle.published_at >= cutoff)
            .order_by(NewsArticle.published_at.desc())
            .limit(max_articles)
        )
        articles = list(sess.exec(stmt))

    if len(articles) < 5:
        logger.info("Not enough recent articles (%d) for hotspot analysis", len(articles))
        return []

    user_msg = (
        f"Here are {len(articles)} recent financial news items, newest first. "
        f"Cluster them into the top market hotspots:\n\n{_format_articles(articles)}"
    )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            output_config={
                "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}
            },
            messages=[{"role": "user", "content": user_msg}],
        )
    except anthropic.APIError as exc:
        logger.exception("Hotspot Claude call failed: %s", exc)
        return []

    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        logger.error("Hotspot JSON parse failed: %s", text[:200])
        return []

    hotspots_data = parsed.get("hotspots", [])

    # Persist
    saved = []
    with Session(engine) as sess:
        for hs in hotspots_data:
            idxs = hs.get("article_indexes", [])
            urls = "\n".join(articles[i].url for i in idxs if 0 <= i < len(articles))
            row = Hotspot(
                title=hs.get("title", "")[:200],
                summary=hs.get("summary", ""),
                tickers=",".join(hs.get("tickers", [])),
                sentiment=hs.get("sentiment", "neutral"),
                article_count=len(idxs),
                article_urls=urls,
            )
            sess.add(row)
            saved.append(hs)
        sess.commit()

    logger.info(
        "Hotspot analysis: %d hotspots from %d articles (cache_read=%d, cache_write=%d)",
        len(saved),
        len(articles),
        response.usage.cache_read_input_tokens,
        response.usage.cache_creation_input_tokens,
    )
    return saved
