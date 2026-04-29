import Link from "next/link";

import { Card, ChangeBadge } from "@/components/Card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

const TREND_LABEL: Record<string, string> = {
  strong_uptrend: "Strong ↑",
  uptrend: "↑",
  neutral: "—",
  downtrend: "↓",
  strong_downtrend: "Strong ↓",
};

export default async function StocksPage() {
  let watchlist;
  try {
    watchlist = await api.watchlist();
  } catch {
    return <div className="text-zinc-400">Backend unreachable.</div>;
  }

  return (
    <Card title="Watchlist">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-zinc-500">
            <tr className="border-b border-zinc-800">
              <th className="py-2">Symbol</th>
              <th className="py-2">Price</th>
              <th className="py-2">Change</th>
              <th className="py-2">RSI</th>
              <th className="py-2">Trend</th>
              <th className="py-2">52w Range</th>
              <th className="py-2">P/E</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {watchlist.map((s) => (
              <tr key={s.symbol} className="hover:bg-zinc-900/40">
                <td className="py-2.5">
                  <Link href={`/stocks/${s.symbol}`} className="font-medium hover:text-emerald-400">
                    {s.symbol}
                  </Link>
                </td>
                <td className="py-2.5 text-zinc-300">${s.price.toFixed(2)}</td>
                <td className="py-2.5">
                  <ChangeBadge pct={s.change_pct} />
                </td>
                <td className="py-2.5 text-zinc-400">{s.rsi_14 ? s.rsi_14.toFixed(1) : "—"}</td>
                <td className="py-2.5 text-zinc-400">{TREND_LABEL[s.trend?.trend ?? "neutral"]}</td>
                <td className="py-2.5 text-zinc-400">
                  {s.trend?.range_pos != null ? `${(s.trend.range_pos * 100).toFixed(0)}%` : "—"}
                </td>
                <td className="py-2.5 text-zinc-400">{s.pe_ratio ? s.pe_ratio.toFixed(1) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
