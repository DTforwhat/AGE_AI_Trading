import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "AGE AI Trading",
  description: "Financial news, hotspots, and stock analysis dashboard",
};

const NAV = [
  { href: "/", label: "Dashboard" },
  { href: "/news", label: "News" },
  { href: "/hotspots", label: "Hotspots" },
  { href: "/stocks", label: "Stocks" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-zinc-800 bg-zinc-900/60 backdrop-blur">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-lg font-semibold tracking-tight">
              AGE <span className="text-emerald-400">AI Trading</span>
            </Link>
            <nav className="flex gap-6 text-sm">
              {NAV.map((n) => (
                <Link key={n.href} href={n.href} className="text-zinc-400 hover:text-zinc-100">
                  {n.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
