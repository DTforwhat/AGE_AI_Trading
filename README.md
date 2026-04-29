# AGE AI Trading

Personal financial dashboard that aggregates real-time news from major sources, clusters market hotspots with Claude, tracks watchlist stocks with technical indicators, and surfaces SEC filings (13F holdings, Form 4 insider trades) — all using **free-tier APIs only**.

## Features

- **News aggregation** — pulls from 10+ free RSS feeds (Yahoo Finance, CNBC, MarketWatch, Reuters, WSJ, FT, Investing.com, Seeking Alpha) plus optional Finnhub & NewsAPI free tiers
- **Hotspot analysis** — Claude Haiku 4.5 clusters recent news into 2–6 market hotspots with sentiment, affected tickers, and source articles
- **Stock trends** — RSI(14), SMA 20/50/200, 52-week range position, multi-tier trend signal
- **Earnings tracking** — historical EPS estimate vs actual + upcoming reports
- **SEC filings** — 13F-HR (institutional holdings), Form 4 (insider trades), 8-K, 10-Q, 10-K via EDGAR
- **Charts** — 6-month price history per ticker

## Stack

- **Backend** — Python 3.11 + FastAPI + SQLModel (SQLite) + APScheduler
- **Frontend** — Next.js 15 + Tailwind + Recharts
- **Data sources** — yfinance, RSS, Finnhub free, NewsAPI free, SEC EDGAR
- **Analysis** — Anthropic API (Claude Haiku 4.5)

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY (required for hotspot analysis)
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for Swagger UI.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:3000`.

## Required Configuration

Only `ANTHROPIC_API_KEY` is required (for hotspot clustering). Everything else is optional:

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | yes | Hotspot clustering via Claude Haiku 4.5 |
| `SEC_USER_AGENT` | yes | SEC EDGAR requires a contact identifier (your name + email) |
| `FINNHUB_API_KEY` | no | Adds Finnhub-curated news + earnings calendar (60 req/min free) |
| `NEWSAPI_KEY` | no | Supplementary business headlines (100 req/day free) |
| `WATCHLIST` | no | Comma-separated tickers (default: major US tech + indices) |

## Cost Estimate

Running the default config:

- **Claude API** — ~$2–8/month if hotspot analysis runs hourly with prompt caching
- All data sources are free

## Architecture

```
backend/
├── app/
│   ├── config.py            # Settings (pydantic-settings)
│   ├── db.py                # SQLite + SQLModel engine
│   ├── models.py            # NewsArticle, StockSnapshot, Hotspot, EarningsEvent
│   ├── main.py              # FastAPI entry + lifespan + CORS
│   ├── scheduler.py         # APScheduler jobs
│   ├── sources/
│   │   ├── rss.py           # 10 free RSS feeds + ticker extraction
│   │   ├── finnhub.py       # Finnhub free-tier (news, earnings calendar)
│   │   ├── newsapi.py       # NewsAPI free-tier
│   │   ├── yfinance_src.py  # Prices, fundamentals, history, earnings
│   │   ├── edgar.py         # SEC EDGAR (13F, Form 4, 8-K, etc.)
│   │   └── aggregator.py    # Orchestrates news + price + earnings refresh
│   ├── analysis/
│   │   ├── hotspot.py       # Claude-powered news clustering with prompt caching
│   │   └── trends.py        # SMA stack + RSI bucket + range position
│   └── api/
│       ├── news.py          # GET /news, POST /news/refresh
│       ├── hotspots.py      # GET /hotspots, POST /hotspots/refresh
│       ├── stocks.py        # GET /stocks/watchlist, GET /stocks/{symbol}
│       └── dashboard.py     # GET /dashboard
└── pyproject.toml

frontend/
├── app/
│   ├── layout.tsx           # Header + nav
│   ├── page.tsx             # Dashboard (top movers, hotspots, earnings)
│   ├── news/page.tsx        # News feed with hours/ticker filters
│   ├── hotspots/page.tsx    # Hotspot cards with sentiment + sources
│   └── stocks/
│       ├── page.tsx         # Watchlist table
│       └── [symbol]/page.tsx # Per-stock detail with chart, news, filings
├── components/
│   ├── Card.tsx             # Card, ChangeBadge, SentimentPill
│   └── PriceChart.tsx       # Recharts line chart
└── lib/api.ts               # Typed API client
```

## Scheduler Defaults

Background jobs (configurable via `.env`):

- **News refresh** — every 15 min
- **Price snapshots** — every 10 min
- **Hotspot analysis** — every 60 min
- **Earnings dates** — every 12 hr

## Manual Triggers (REST)

```
POST /news/refresh        # pull all news sources now
POST /hotspots/refresh    # run Claude hotspot clustering now
GET  /stocks/watchlist    # latest snapshots for all watchlist tickers
GET  /stocks/{symbol}     # full detail (profile, chart, news, filings, earnings)
GET  /dashboard           # summary for the homepage
```

## Upgrading to Paid Sources

When you hit a wall, the easiest upgrades (in order):

1. **Tiingo** ($10/mo) — better historical news + fundamentals
2. **Polygon.io Starter** ($29/mo) — real-time prices, no rate limits
3. **Finnhub Pro** ($50/mo) — sentiment scores, analyst ratings

Each integration would be a new file under `app/sources/` following the same shape as the existing modules.

## Notes & Limitations

- **13F filings have a 45-day delay** — this is a hard SEC rule, not a technical limit
- **yfinance can be rate-limited** during heavy use — fine for personal scale
- **NewsAPI free** only returns last 24 hours of news
- **No A-share support yet** — easy to add via AKShare/Tushare under `app/sources/`

## License

Personal project. No license declared.
