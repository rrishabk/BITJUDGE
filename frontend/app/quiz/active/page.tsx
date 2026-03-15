import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const mcqs = [
  {
    question: "Which traversal is ideal for shortest path in an unweighted graph?",
    options: ["DFS", "BFS", "Dijkstra", "Prim"],
  },
];

export default function ActiveQuizPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.4em] text-accent">Active Quiz</p>
          <h1 className="mt-2 text-4xl font-black">DSA Mid-Sem Sprint</h1>
        </div>
        <Button>Submit Quiz</Button>
      </div>
      <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <p className="text-sm uppercase tracking-[0.35em] text-accent">MCQ</p>
          <h2 className="mt-3 text-xl font-semibold">{mcqs[0].question}</h2>
          <div className="mt-4 grid gap-3">
            {mcqs[0].options.map((option) => (
              <button key={option} className="rounded-2xl border border-border bg-black/30 p-3 text-left transition hover:border-accent">
                {option}
              </button>
            ))}
          </div>
        </Card>
        <Card>
          <p className="text-sm uppercase tracking-[0.35em] text-accent">Coding</p>
          <h2 className="mt-3 text-xl font-semibold">Implement Dijkstra using adjacency list.</h2>
          <div className="mt-4 grid gap-4 lg:grid-cols-[0.6fr_0.4fr]">
            <textarea className="min-h-[320px] rounded-3xl border border-border bg-[#050505] p-4 font-mono text-sm text-zinc-200 outline-none" defaultValue={'# write your solution here'} />
            <div className="space-y-4">
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Input</p>
                <p className="mt-2 font-mono text-sm">5 6\n1 2 7\n1 3 9</p>
              </div>
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">Expected Output</p>
                <p className="mt-2 font-mono text-sm">0 7 9 20 20</p>
              </div>
              <Button className="w-full">Run with Judge0</Button>
            </div>
          </div>
        </Card>
      </section>
    </main>
  );
}
