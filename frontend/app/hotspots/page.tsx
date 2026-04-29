import Link from "next/link";

import { Card, SentimentPill } from "@/components/Card";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HotspotsPage() {
  let hotspots;
  try {
    hotspots = await api.hotspots(50);
  } catch {
    return <div className="text-zinc-400">Backend unreachable.</div>;
  }

  return (
    <Card title="Market Hotspots">
      <p className="mb-4 text-sm text-zinc-500">
        Clustered by Claude every {process.env.NEXT_PUBLIC_HOTSPOT_INTERVAL || "60"} min from recent news. POST{" "}
        <code>/hotspots/refresh</code> to run on demand.
      </p>
      <ul className="space-y-4">
        {hotspots.length === 0 && <li className="text-sm text-zinc-500">No hotspots yet.</li>}
        {hotspots.map((h) => (
          <li key={h.id} className="rounded-lg border border-zinc-800 p-4">
            <div className="flex items-start justify-between gap-3">
              <h3 className="text-lg font-semibold leading-tight">{h.title}</h3>
              <SentimentPill sentiment={h.sentiment} />
            </div>
            <p className="mt-2 text-sm text-zinc-300">{h.summary}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
              <span>{h.article_count} articles</span>
              <span>·</span>
              <time>{new Date(h.created_at).toLocaleString()}</time>
              {h.tickers.length > 0 && <span>·</span>}
              {h.tickers.map((t) => (
                <Link
                  key={t}
                  href={`/stocks/${t}`}
                  className="rounded bg-zinc-800 px-1.5 py-0.5 text-zinc-300 hover:bg-zinc-700"
                >
                  {t}
                </Link>
              ))}
            </div>
            {h.article_urls.length > 0 && (
              <details className="mt-3 text-xs">
                <summary className="cursor-pointer text-zinc-500 hover:text-zinc-300">
                  Source articles ({h.article_urls.length})
                </summary>
                <ul className="mt-2 space-y-1">
                  {h.article_urls.map((u) => (
                    <li key={u}>
                      <a
                        href={u}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-zinc-400 hover:text-emerald-400"
                      >
                        {u}
                      </a>
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </li>
        ))}
      </ul>
    </Card>
  );
}
