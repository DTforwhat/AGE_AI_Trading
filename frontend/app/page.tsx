import Link from "next/link";

import { Card, ChangeBadge, SentimentPill } from "@/components/Card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let data;
  try {
    data = await api.dashboard();
  } catch {
    return (
      <div className="text-zinc-400">
        Backend unreachable at <code>{process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</code>. Start the
        FastAPI server and reload.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
      <div className="grid grid-cols-3 gap-4 lg:col-span-3">
        <Stat label="Articles · 24h" value={data.articles_24h.toString()} />
        <Stat label="Watchlist size" value={data.watchlist_size.toString()} />
        <Stat label="Hotspots · 7d" value={data.recent_hotspots.length.toString()} />
      </div>

      <Card title="Top Movers" action={<Link href="/stocks" className="text-xs text-zinc-400 hover:text-zinc-100">all →</Link>}>
        <ul className="divide-y divide-zinc-800 text-sm">
          {data.top_movers.length === 0 && <li className="py-3 text-zinc-500">No snapshots yet — wait a minute.</li>}
          {data.top_movers.map((m) => (
            <li key={m.symbol} className="flex items-center justify-between py-2">
              <Link href={`/stocks/${m.symbol}`} className="font-medium hover:text-emerald-400">
                {m.symbol}
              </Link>
              <div className="flex items-center gap-3">
                <span className="text-zinc-400">${m.price.toFixed(2)}</span>
                <ChangeBadge pct={m.change_pct} />
              </div>
            </li>
          ))}
        </ul>
      </Card>

      <Card
        title="Recent Hotspots"
        action={<Link href="/hotspots" className="text-xs text-zinc-400 hover:text-zinc-100">all →</Link>}
      >
        <ul className="space-y-3 text-sm">
          {data.recent_hotspots.length === 0 && (
            <li className="text-zinc-500">No hotspots yet — runs hourly. POST /hotspots/refresh to trigger now.</li>
          )}
          {data.recent_hotspots.map((h) => (
            <li key={h.id} className="rounded-lg border border-zinc-800 p-3">
              <div className="flex items-start justify-between gap-3">
                <div className="font-medium">{h.title}</div>
                <SentimentPill sentiment={h.sentiment} />
              </div>
              <p className="mt-1 text-zinc-400">{h.summary}</p>
              {h.tickers.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {h.tickers.map((t) => (
                    <Link
                      key={t}
                      href={`/stocks/${t}`}
                      className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300 hover:bg-zinc-700"
                    >
                      {t}
                    </Link>
                  ))}
                </div>
              )}
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Upcoming Earnings">
        <ul className="divide-y divide-zinc-800 text-sm">
          {data.upcoming_earnings.length === 0 && <li className="py-3 text-zinc-500">No earnings within range.</li>}
          {data.upcoming_earnings.map((e, i) => (
            <li key={`${e.symbol}-${i}`} className="flex items-center justify-between py-2">
              <Link href={`/stocks/${e.symbol}`} className="font-medium hover:text-emerald-400">
                {e.symbol}
              </Link>
              <div className="text-zinc-400">
                {new Date(e.report_date).toLocaleDateString()}
                {e.eps_estimate !== null && ` · est ${e.eps_estimate}`}
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5">
      <div className="text-xs uppercase tracking-wider text-zinc-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
    </div>
  );
}
