import { ActivityChart } from "@/components/activity-chart";
import { Card } from "@/components/ui/card";
import { studentStats } from "@/lib/mock-data";

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.4em] text-accent">Student Dashboard</p>
        <h1 className="mt-2 text-4xl font-black">Performance overview</h1>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <p className="text-sm text-zinc-500">Problems Solved</p>
          <p className="mt-3 text-4xl font-bold">{studentStats.solved}</p>
        </Card>
        <Card>
          <p className="text-sm text-zinc-500">Quiz Score</p>
          <p className="mt-3 text-4xl font-bold">{studentStats.quizAverage}%</p>
        </Card>
        <Card>
          <p className="text-sm text-zinc-500">Weak Topics</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {studentStats.weakTopics.map((topic) => (
              <span key={topic} className="rounded-full border border-accent/30 px-3 py-1 text-xs uppercase tracking-[0.18em] text-accent">
                {topic}
              </span>
            ))}
          </div>
        </Card>
        <Card>
          <p className="text-sm text-zinc-500">Active Quiz</p>
          <p className="mt-3 text-2xl font-bold">{studentStats.activeQuiz.timeLeft}</p>
          <p className="mt-2 text-sm text-zinc-400">{studentStats.activeQuiz.title}</p>
        </Card>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <p className="text-sm uppercase tracking-[0.35em] text-accent">Activity Graph</p>
          <h2 className="mt-2 text-2xl font-bold">Weekly coding rhythm</h2>
          <div className="mt-6">
            <ActivityChart data={studentStats.activity} />
          </div>
        </Card>
        <Card>
          <p className="text-sm uppercase tracking-[0.35em] text-accent">Recent Quiz History</p>
          <div className="mt-6 space-y-4">
            {studentStats.previousQuizzes.map((quiz) => (
              <div key={quiz.title} className="rounded-2xl border border-border bg-black/30 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-semibold">{quiz.title}</p>
                    <p className="text-sm text-zinc-500">{quiz.date}</p>
                  </div>
                  <p className="text-2xl font-bold text-accent">{quiz.score}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </main>
  );
}
