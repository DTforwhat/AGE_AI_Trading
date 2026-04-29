from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class NewsArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)
    title: str
    url: str = Field(unique=True, index=True)
    summary: str = ""
    published_at: datetime = Field(index=True)
    tickers: str = ""  # comma-separated symbols inferred from content
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class StockSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    price: float
    change_pct: float
    volume: int = 0
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    rsi_14: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Hotspot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    summary: str
    tickers: str = ""  # comma-separated
    sentiment: str = "neutral"  # bullish | bearish | neutral
    article_count: int = 0
    article_urls: str = ""  # newline-separated
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class EarningsEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    report_date: datetime = Field(index=True)
    eps_estimate: Optional[float] = None
    eps_actual: Optional[float] = None
    revenue_estimate: Optional[float] = None
    revenue_actual: Optional[float] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
