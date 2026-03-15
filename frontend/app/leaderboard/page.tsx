import { Card } from "@/components/ui/card";
import { leaderboardRows } from "@/lib/mock-data";

function rankClass(rank: number) {
  if (rank === 1) return "border-[#f5c15d] bg-[#2b1d08] text-[#ffd27a]";
  if (rank === 2) return "border-zinc-500 bg-zinc-800/70 text-zinc-100";
  if (rank === 3) return "border-[#9d5d2b] bg-[#2a1608] text-[#ffb577]";
  return "border-border bg-black/20 text-zinc-300";
}

export default function LeaderboardPage() {
  const topThree = leaderboardRows.slice(0, 3);
  const rest = leaderboardRows.slice(3);

  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.4em] text-accent">Leaderboard</p>
          <h1 className="mt-2 text-4xl font-black">Campus ranking board</h1>
        </div>
        <div className="flex gap-3 text-xs uppercase tracking-[0.25em] text-zinc-400">
          <span className="rounded-full border border-accent/30 px-4 py-2 text-accent">Score First</span>
          <span className="rounded-full border border-border px-4 py-2">LeetCode-style View</span>
        </div>
      </div>

      <section className="mb-6 grid gap-4 lg:grid-cols-3">
        {topThree.map((student) => (
          <Card key={student.rank} className="relative overflow-hidden border-accent/20 bg-gradient-to-b from-black to-[#14110b]">
            <div className="absolute right-4 top-4 text-6xl font-black text-accent/10">#{student.rank}</div>
            <p className="text-xs uppercase tracking-[0.35em] text-accent">Top Performer</p>
            <h2 className="mt-4 text-2xl font-bold">{student.name}</h2>
            <div className="mt-6 grid grid-cols-3 gap-3 text-center">
              <div className="rounded-2xl border border-border bg-black/30 p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Solved</p>
                <p className="mt-2 text-2xl font-bold">{student.problemsSolved}</p>
              </div>
              <div className="rounded-2xl border border-border bg-black/30 p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Score</p>
                <p className="mt-2 text-2xl font-bold text-accent">{student.score}</p>
              </div>
              <div className="rounded-2xl border border-border bg-black/30 p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Streak</p>
                <p className="mt-2 text-2xl font-bold">{student.streak}</p>
              </div>
            </div>
          </Card>
        ))}
      </section>

      <Card className="overflow-hidden p-0">
        <div className="grid grid-cols-[88px_minmax(220px,1.6fr)_1fr_1fr_0.9fr] border-b border-border bg-[#141414] px-6 py-4 text-xs font-semibold uppercase tracking-[0.25em] text-zinc-500">
          <span>Rank</span>
          <span>Student Name</span>
          <span>Problems Solved</span>
          <span>Score</span>
          <span>Streak</span>
        </div>
        <div>
          {[...topThree, ...rest].map((student) => (
            <div
              key={student.rank}
              className="grid grid-cols-[88px_minmax(220px,1.6fr)_1fr_1fr_0.9fr] items-center border-b border-border/80 px-6 py-4 transition hover:bg-[#141414]"
            >
              <div>
                <span className={`inline-flex min-w-12 items-center justify-center rounded-full border px-3 py-2 text-sm font-bold ${rankClass(student.rank)}`}>
                  {student.rank}
                </span>
              </div>
              <div className="pr-4">
                <p className="text-base font-semibold text-foreground">{student.name}</p>
                <p className="text-sm text-zinc-500">BITJUDGE competitor</p>
              </div>
              <div>
                <p className="text-lg font-semibold text-zinc-100">{student.problemsSolved}</p>
              </div>
              <div>
                <p className="text-lg font-semibold text-accent">{student.score}</p>
              </div>
              <div>
                <span className="rounded-full border border-accent/30 bg-accent/10 px-3 py-2 text-sm font-semibold text-accent">
                  {student.streak} days
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </main>
  );
}
