import Link from "next/link";
import { notFound } from "next/navigation";

import { Card, ChangeBadge } from "@/components/Card";
import { PriceChart } from "@/components/PriceChart";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

const TREND_LABEL: Record<string, string> = {
  strong_uptrend: "Strong uptrend",
  uptrend: "Uptrend",
  neutral: "Neutral",
  downtrend: "Downtrend",
  strong_downtrend: "Strong downtrend",
};

export default async function StockDetailPage({ params }: { params: Promise<{ symbol: string }> }) {
  const { symbol } = await params;
  let detail;
  try {
    detail = await api.stock(symbol);
  } catch {
    notFound();
  }
  if (!detail) notFound();

  const s = detail.snapshot;
  const t = detail.trend;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-semibold">
          {detail.profile.name} <span className="text-zinc-500">· {s.symbol}</span>
        </h1>
        <div className="mt-1 text-sm text-zinc-500">
          {detail.profile.sector && `${detail.profile.sector} · `}
          {detail.profile.industry}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Price" value={`$${s.price.toFixed(2)}`} sub={<ChangeBadge pct={s.change_pct} />} />
        <Stat label="RSI 14" value={s.rsi_14 ? s.rsi_14.toFixed(1) : "—"} sub={<span className="text-zinc-500">{t?.rsi_state ?? ""}</span>} />
        <Stat label="Trend" value={TREND_LABEL[t?.trend ?? "neutral"]} />
        <Stat
          label="52w Range"
          value={
            s.fifty_two_week_low && s.fifty_two_week_high
              ? `$${s.fifty_two_week_low.toFixed(0)} – $${s.fifty_two_week_high.toFixed(0)}`
              : "—"
          }
          sub={t?.range_pos != null ? <span className="text-zinc-500">{(t.range_pos * 100).toFixed(0)}% of range</span> : null}
        />
      </div>

      <Card title="Price · 6 months">
        <PriceChart data={detail.history.map((h) => ({ date: h.date, close: h.close }))} />
      </Card>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Card
          title="Recent News"
          action={
            <Link href={`/news?ticker=${s.symbol}`} className="text-xs text-zinc-400 hover:text-zinc-100">
              all →
            </Link>
          }
        >
          <ul className="divide-y divide-zinc-800 text-sm">
            {detail.news.length === 0 && <li className="py-3 text-zinc-500">No news in the last 14 days.</li>}
            {detail.news.map((n) => (
              <li key={n.url} className="py-2">
                <a href={n.url} target="_blank" rel="noopener noreferrer" className="hover:text-emerald-400">
                  {n.title}
                </a>
                <div className="mt-0.5 text-xs text-zinc-500">
                  {n.source} · {new Date(n.published_at).toLocaleString()}
                </div>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Earnings History">
          <ul className="divide-y divide-zinc-800 text-sm">
            {detail.earnings.length === 0 && <li className="py-3 text-zinc-500">No earnings data.</li>}
            {detail.earnings.map((e) => (
              <li key={e.report_date} className="flex items-center justify-between py-2">
                <span className="text-zinc-300">{new Date(e.report_date).toLocaleDateString()}</span>
                <span className="text-zinc-400">
                  {e.eps_actual !== null ? `actual ${e.eps_actual}` : "pending"}
                  {e.eps_estimate !== null && ` · est ${e.eps_estimate}`}
                </span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="SEC Filings (EDGAR)">
          <ul className="divide-y divide-zinc-800 text-sm">
            {detail.filings.length === 0 && <li className="py-3 text-zinc-500">No filings found.</li>}
            {detail.filings.slice(0, 12).map((f) => (
              <li key={f.accession} className="flex items-center justify-between gap-3 py-2">
                <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs">{f.form}</span>
                <span className="flex-1 text-zinc-400">{f.filing_date}</span>
                {f.url && (
                  <a href={f.url} target="_blank" rel="noopener noreferrer" className="text-xs text-emerald-400 hover:underline">
                    open
                  </a>
                )}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-zinc-500">13F filings are filed 45 days after quarter-end (SEC rule).</p>
        </Card>

        <Card title="Fundamentals">
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <Fundamental label="Market cap" value={fmtBig(s.market_cap)} />
            <Fundamental label="P/E (TTM)" value={s.pe_ratio?.toFixed(2) ?? "—"} />
            <Fundamental label="SMA 20" value={s.sma_20?.toFixed(2) ?? "—"} />
            <Fundamental label="SMA 50" value={s.sma_50?.toFixed(2) ?? "—"} />
            <Fundamental label="SMA 200" value={s.sma_200?.toFixed(2) ?? "—"} />
            <Fundamental label="Volume" value={s.volume ? s.volume.toLocaleString() : "—"} />
          </dl>
          {detail.profile.summary && (
            <p className="mt-4 text-xs leading-relaxed text-zinc-400">{detail.profile.summary}</p>
          )}
        </Card>
      </div>
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="text-xs uppercase tracking-wider text-zinc-500">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
      {sub && <div className="text-sm">{sub}</div>}
    </div>
  );
}

function Fundamental({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between">
      <dt className="text-zinc-500">{label}</dt>
      <dd className="text-zinc-200">{value}</dd>
    </div>
  );
}

function fmtBig(n: number | null | undefined): string {
  if (!n) return "—";
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n.toLocaleString()}`;
}
