import Link from "next/link";

import { Card } from "@/components/ui/card";
import { studentStats } from "@/lib/mock-data";

export default function QuizPage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.4em] text-accent">Quiz Center</p>
        <h1 className="mt-2 text-4xl font-black">Active and previous quiz access</h1>
      </div>
      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="grid-surface">
          <p className="text-sm uppercase tracking-[0.3em] text-accent">Active Quiz</p>
          <h2 className="mt-3 text-3xl font-bold">{studentStats.activeQuiz.title}</h2>
          <p className="mt-2 text-zinc-400">{studentStats.activeQuiz.questions} questions live now. Time left: {studentStats.activeQuiz.timeLeft}</p>
          <Link href="/quiz/active" className="mt-6 inline-flex rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-black">
            Active Quiz
          </Link>
        </Card>
        <Card>
          <p className="text-sm uppercase tracking-[0.3em] text-accent">Previous Quizzes</p>
          <div className="mt-4 space-y-3">
            {studentStats.previousQuizzes.map((quiz) => (
              <div key={quiz.title} className="rounded-2xl border border-border bg-black/30 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{quiz.title}</p>
                    <p className="text-sm text-zinc-500">{quiz.date}</p>
                  </div>
                  <p className="text-accent">{quiz.score}</p>
                </div>
              </div>
            ))}
          </div>
          <button type="button" className="mt-6 rounded-2xl border border-accent/30 px-5 py-3 text-sm font-semibold text-accent">
            Previous Quiz
          </button>
        </Card>
      </section>
    </main>
  );
}
