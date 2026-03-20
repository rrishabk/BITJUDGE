import { Card } from "@/components/ui/card";
import { adminStats } from "@/lib/mock-data";

export default function AdminDashboardPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.4em] text-accent">Admin Dashboard</p>
        <h1 className="mt-2 text-4xl font-black">Quiz operations and platform analytics</h1>
      </div>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card><p className="text-sm text-zinc-500">Registered Students</p><p className="mt-2 text-4xl font-bold">{adminStats.totalUsers}</p></Card>
        <Card><p className="text-sm text-zinc-500">Active Users</p><p className="mt-2 text-4xl font-bold">{adminStats.activeUsers}</p></Card>
        <Card><p className="text-sm text-zinc-500">Live Participants</p><p className="mt-2 text-4xl font-bold">{adminStats.liveQuizParticipants}</p></Card>
        <Card><p className="text-sm text-zinc-500">Completion Rate</p><p className="mt-2 text-4xl font-bold">{adminStats.completionRate}%</p></Card>
      </section>
      <section className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <p className="text-sm uppercase tracking-[0.35em] text-accent">Create Quiz</p>
          <div className="mt-4 grid gap-3">
            <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="Quiz Title" />
            <div className="grid gap-3 md:grid-cols-2">
              <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="Start Time" />
              <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="End Time" />
            </div>
            <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="Number of Questions" />
          </div>
        </Card>
        <Card>
          <p className="text-sm uppercase tracking-[0.35em] text-accent">Leaderboards</p>
          <div className="mt-4 space-y-3">
            {[
              ["Aditi", 460],
              ["Rohan", 430],
              ["Mehul", 410],
            ].map(([name, score], index) => (
              <div key={name} className="flex items-center justify-between rounded-2xl bg-black/30 p-4">
                <p className="font-semibold">#{index + 1} {name}</p>
                <p className="text-accent">{score}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </main>
  );
}
