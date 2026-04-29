import { ReactNode } from "react";

export function Card({
  title,
  action,
  children,
}: {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5">
      {(title || action) && (
        <div className="mb-3 flex items-center justify-between">
          {title && <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">{title}</h2>}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function ChangeBadge({ pct }: { pct: number }) {
  const positive = pct >= 0;
  return (
    <span className={positive ? "text-bull" : "text-bear"}>
      {positive ? "+" : ""}
      {pct.toFixed(2)}%
    </span>
  );
}

export function SentimentPill({ sentiment }: { sentiment: string }) {
  const cls =
    sentiment === "bullish"
      ? "bg-bull/15 text-bull"
      : sentiment === "bearish"
        ? "bg-bear/15 text-bear"
        : "bg-zinc-700/40 text-zinc-300";
  return <span className={`inline-block rounded px-2 py-0.5 text-xs ${cls}`}>{sentiment}</span>;
}
