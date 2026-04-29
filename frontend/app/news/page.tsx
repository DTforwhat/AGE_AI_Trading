import Link from "next/link";

import { Card } from "@/components/Card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function NewsPage({
  searchParams,
}: {
  searchParams: Promise<{ ticker?: string; hours?: string }>;
}) {
  const sp = await searchParams;
  const ticker = sp.ticker;
  const hours = Number(sp.hours) || 24;

  let news;
  try {
    news = await api.news({ hours, ticker, limit: 200 });
  } catch {
    return <div className="text-zinc-400">Backend unreachable.</div>;
  }

  return (
    <Card
      title={`News${ticker ? ` · ${ticker}` : ""} · last ${hours}h`}
      action={
        <div className="flex gap-2 text-xs">
          {[12, 24, 48, 168].map((h) => (
            <Link
              key={h}
              href={`/news?hours=${h}${ticker ? `&ticker=${ticker}` : ""}`}
              className={
                h === hours
                  ? "rounded bg-zinc-800 px-2 py-1 text-zinc-100"
                  : "rounded px-2 py-1 text-zinc-400 hover:bg-zinc-800/50"
              }
            >
              {h}h
            </Link>
          ))}
        </div>
      }
    >
      <ul className="divide-y divide-zinc-800">
        {news.length === 0 && <li className="py-6 text-sm text-zinc-500">No articles yet. Run POST /news/refresh.</li>}
        {news.map((n) => (
          <li key={n.id} className="py-3">
            <a href={n.url} target="_blank" rel="noopener noreferrer" className="block hover:text-emerald-400">
              <div className="font-medium leading-snug">{n.title}</div>
            </a>
            {n.summary && <p className="mt-1 text-sm text-zinc-400">{n.summary}</p>}
            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
              <span>{n.source}</span>
              <span>·</span>
              <time>{new Date(n.published_at).toLocaleString()}</time>
              {n.tickers.length > 0 && (
                <>
                  <span>·</span>
                  {n.tickers.map((t) => (
                    <Link
                      key={t}
                      href={`/stocks/${t}`}
                      className="rounded bg-zinc-800 px-1.5 py-0.5 hover:bg-zinc-700"
                    >
                      {t}
                    </Link>
                  ))}
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
