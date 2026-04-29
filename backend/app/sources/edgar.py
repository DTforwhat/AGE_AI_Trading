"""SEC EDGAR access for institutional holdings (13F) and insider trades (Form 4).

Fully free; only requires a User-Agent identifying the requester.
Note: 13F filings are filed quarterly with a 45-day delay (SEC rule).
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BASE = "https://data.sec.gov"


def _headers() -> dict[str, str]:
    return {"User-Agent": settings.sec_user_agent, "Accept": "application/json"}


def get_cik_for_ticker(ticker: str) -> Optional[str]:
    """Look up an issuer's 10-digit CIK from a ticker."""
    try:
        with httpx.Client(timeout=10.0, headers=_headers()) as client:
            resp = client.get("https://www.sec.gov/files/company_tickers.json")
            resp.raise_for_status()
            data = resp.json()
            for entry in data.values():
                if entry.get("ticker", "").upper() == ticker.upper():
                    return str(entry["cik_str"]).zfill(10)
    except httpx.HTTPError as exc:
        logger.warning("EDGAR CIK lookup failed for %s: %s", ticker, exc)
    return None


def fetch_recent_filings(ticker: str, form_types: tuple[str, ...] = ("13F-HR", "4", "8-K")) -> list[dict]:
    """Recent SEC filings for a ticker, filtered by form type."""
    cik = get_cik_for_ticker(ticker)
    if not cik:
        return []
    try:
        with httpx.Client(timeout=10.0, headers=_headers()) as client:
            resp = client.get(f"{BASE}/submissions/CIK{cik}.json")
            resp.raise_for_status()
            data = resp.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accession = recent.get("accessionNumber", [])
            primary_doc = recent.get("primaryDocument", [])
            results = []
            for i, form in enumerate(forms):
                if form not in form_types:
                    continue
                acc_clean = accession[i].replace("-", "") if i < len(accession) else ""
                doc = primary_doc[i] if i < len(primary_doc) else ""
                results.append(
                    {
                        "ticker": ticker,
                        "form": form,
                        "filing_date": dates[i] if i < len(dates) else "",
                        "accession": accession[i] if i < len(accession) else "",
                        "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/{doc}"
                        if acc_clean and doc
                        else "",
                    }
                )
                if len(results) >= 20:
                    break
            return results
    except httpx.HTTPError as exc:
        logger.warning("EDGAR filings fetch failed for %s: %s", ticker, exc)
        return []
