const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: "POST", cache: "no-store" });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export type NewsItem = {
  id: number;
  source: string;
  title: string;
  url: string;
  summary: string;
  published_at: string;
  tickers: string[];
};

export type HotspotItem = {
  id: number;
  title: string;
  summary: string;
  tickers: string[];
  sentiment: "bullish" | "bearish" | "neutral";
  article_count: number;
  article_urls: string[];
  created_at: string;
};

export type StockSnap = {
  symbol: string;
  price: number;
  change_pct: number;
  volume?: number;
  market_cap?: number | null;
  pe_ratio?: number | null;
  fifty_two_week_high?: number | null;
  fifty_two_week_low?: number | null;
  rsi_14?: number | null;
  sma_20?: number | null;
  sma_50?: number | null;
  sma_200?: number | null;
  trend?: {
    trend: string;
    rsi_state: string | null;
    range_pos: number | null;
    rsi: number | null;
  };
};

export type DashboardSummary = {
  articles_24h: number;
  watchlist_size: number;
  top_movers: { symbol: string; price: number; change_pct: number }[];
  recent_hotspots: HotspotItem[];
  upcoming_earnings: {
    symbol: string;
    report_date: string;
    eps_estimate: number | null;
  }[];
};

export type StockDetail = {
  profile: {
    symbol: string;
    name: string;
    sector?: string | null;
    industry?: string | null;
    summary?: string;
    website?: string | null;
    employees?: number | null;
  };
  snapshot: StockSnap;
  trend: StockSnap["trend"];
  history: { date: string; open: number; high: number; low: number; close: number; volume: number }[];
  news: { title: string; url: string; source: string; published_at: string }[];
  earnings: { report_date: string; eps_estimate: number | null; eps_actual: number | null }[];
  filings: { ticker: string; form: string; filing_date: string; accession: string; url: string }[];
};

export const api = {
  dashboard: () => get<DashboardSummary>("/dashboard"),
  news: (params: { hours?: number; ticker?: string; limit?: number } = {}) => {
    const q = new URLSearchParams();
    if (params.hours) q.set("hours", String(params.hours));
    if (params.ticker) q.set("ticker", params.ticker);
    if (params.limit) q.set("limit", String(params.limit));
    return get<NewsItem[]>(`/news${q.toString() ? `?${q}` : ""}`);
  },
  refreshNews: () => post<{ new_articles: number }>("/news/refresh"),
  hotspots: (limit = 20) => get<HotspotItem[]>(`/hotspots?limit=${limit}`),
  refreshHotspots: () => post<{ created: number }>("/hotspots/refresh"),
  watchlist: () => get<StockSnap[]>("/stocks/watchlist"),
  stock: (symbol: string) => get<StockDetail>(`/stocks/${symbol}`),
};
