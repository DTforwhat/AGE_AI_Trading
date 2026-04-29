"""FastAPI entry point. Wires routers, scheduler, and DB."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import dashboard, hotspots, news, stocks
from app.config import settings
from app.db import init_db
from app.scheduler import build_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    sched = build_scheduler()
    sched.start()
    app.state.scheduler = sched
    yield
    sched.shutdown(wait=False)


app = FastAPI(title="AGE AI Trading", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(hotspots.router)
app.include_router(stocks.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok", "watchlist": settings.watchlist_tickers}
