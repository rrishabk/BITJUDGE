import Link from "next/link";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/practice", label: "Practice" },
  { href: "/quiz", label: "Quiz" },
  { href: "/leaderboard", label: "Leaderboard" },
  { href: "/profile", label: "Profile" },
];

export function TopNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-black/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <div>
          <Link href="/" className="text-2xl font-extrabold tracking-[0.2em] text-foreground">
            BITJUDGE
          </Link>
          <p className="mt-1 text-[11px] uppercase tracking-[0.38em] text-accent">Powered by BITWISE</p>
        </div>
        <nav className="flex flex-wrap gap-5 text-sm font-medium text-zinc-300">
          {items.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-accent">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
