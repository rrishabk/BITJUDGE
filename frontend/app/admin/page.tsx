"use client";

import {
  Activity,
  BarChart3,
  CheckCircle2,
  Code2,
  Database,
  FileCode2,
  Gauge,
  LayoutDashboard,
  ListChecks,
  Plus,
  SquareCheckBig,
  Trophy,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useMemo, useState } from "react";

import { Card } from "@/components/ui/card";
import { adminStats, questionBank } from "@/lib/mock-data";

const sidebarItems = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Users", icon: Users },
  { label: "Problems", icon: FileCode2 },
  { label: "Quizzes", icon: ListChecks },
  { label: "Leaderboard", icon: Trophy },
  { label: "System Stats", icon: Gauge },
];

const pieColors = ["#f59e0b", "#fb923c", "#facc15", "#fdba74"];
const codingLanguageOptions = ["C++", "Java", "Python", "C"];

export default function AdminPage() {
  const [createdQuiz, setCreatedQuiz] = useState<{ id: number; title: string } | null>({ id: 54, title: "Weekly DSA Arena" });
  const [selectedQuestionType, setSelectedQuestionType] = useState<"mcq" | "coding">("mcq");
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(["C++", "Java", "Python", "C"]);
  const [attachedQuestionIds, setAttachedQuestionIds] = useState<number[]>([101, 201]);

  const reusableQuestions = useMemo(
    () => questionBank.filter((question) => question.type === selectedQuestionType),
    [selectedQuestionType],
  );

  function toggleAttachedQuestion(id: number) {
    setAttachedQuestionIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
    );
  }

  function toggleLanguage(language: string) {
    setSelectedLanguages((current) =>
      current.includes(language)
        ? current.filter((item) => item !== language)
        : [...current, language],
    );
  }

  return (
    <main className="mx-auto flex max-w-7xl gap-6 px-4 py-8 sm:px-6">
      <aside className="hidden w-72 shrink-0 lg:block">
        <div className="sticky top-24 space-y-5 rounded-[32px] border border-border bg-[#101010]/95 p-5 shadow-glow backdrop-blur">
          <div className="rounded-[28px] border border-accent/20 bg-gradient-to-br from-[#241507] to-[#120f0c] p-5">
            <p className="text-xs uppercase tracking-[0.35em] text-accent">Admin Panel</p>
            <h1 className="mt-3 text-3xl font-black text-foreground">BITJUDGE Ops</h1>
            <p className="mt-3 text-sm text-zinc-400">Create quizzes, reuse question banks, and run live coding assessments from one control room.</p>
          </div>
          <nav className="space-y-2">
            {sidebarItems.map(({ label, icon: Icon, active }) => (
              <button
                key={label}
                type="button"
                className={active ? "flex w-full items-center gap-3 rounded-2xl border border-accent/30 bg-accent px-4 py-3 text-left text-sm font-semibold text-black" : "flex w-full items-center gap-3 rounded-2xl border border-border bg-black/20 px-4 py-3 text-left text-sm font-semibold text-zinc-300 transition hover:border-accent/30 hover:text-accent"}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
          <div className="rounded-[24px] border border-border bg-black/30 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-zinc-500">Live Builder</p>
            <p className="mt-2 text-lg font-bold text-foreground">{createdQuiz?.title ?? "No quiz created"}</p>
            <button type="button" className="mt-4 w-full rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-black">
              Publish Quiz
            </button>
          </div>
        </div>
      </aside>

      <section className="min-w-0 flex-1 space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.4em] text-accent">Admin Dashboard</p>
            <h2 className="mt-2 text-4xl font-black text-foreground">Quiz builder and system command center</h2>
          </div>
          <div className="flex gap-3">
            <button type="button" className="rounded-2xl border border-border bg-black/20 px-4 py-3 text-sm font-semibold text-zinc-200">
              Save Draft
            </button>
            <button type="button" className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-black">
              Create Quiz
            </button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border-accent/15 bg-gradient-to-b from-[#18120b] to-[#111111]">
            <p className="text-sm text-zinc-500">Total Users</p>
            <p className="mt-3 text-4xl font-black">{adminStats.totalUsers}</p>
          </Card>
          <Card>
            <p className="text-sm text-zinc-500">Total Problems</p>
            <p className="mt-3 text-4xl font-black">{adminStats.totalProblems}</p>
          </Card>
          <Card>
            <p className="text-sm text-zinc-500">Total Submissions</p>
            <p className="mt-3 text-4xl font-black">{adminStats.totalSubmissions}</p>
          </Card>
          <Card>
            <p className="text-sm text-zinc-500">Active Quiz</p>
            <p className="mt-3 text-2xl font-black">{adminStats.activeQuiz}</p>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <Card className="border-accent/15 bg-[#111111]">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Create Quiz</p>
                <h3 className="mt-2 text-2xl font-bold">Step 1: quiz details</h3>
              </div>
              <Plus className="h-5 w-5 text-accent" />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2 text-sm text-zinc-300 md:col-span-2">
                <span>Quiz title</span>
                <input className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4" placeholder="Weekly Graphs Challenge" />
              </label>
              <label className="space-y-2 text-sm text-zinc-300">
                <span>Start date</span>
                <input type="datetime-local" className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4" />
              </label>
              <label className="space-y-2 text-sm text-zinc-300">
                <span>End date</span>
                <input type="datetime-local" className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4" />
              </label>
              <label className="space-y-2 text-sm text-zinc-300 md:col-span-2">
                <span>Number of questions</span>
                <input type="number" className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4" placeholder="10" />
              </label>
            </div>
            <div className="mt-5 flex items-center justify-between rounded-2xl border border-accent/20 bg-accent/5 px-4 py-3">
              <div>
                <p className="text-sm font-semibold text-foreground">Current quiz context</p>
                <p className="text-sm text-zinc-400">After quiz creation, admins can attach either brand-new or previously created questions.</p>
              </div>
              <button
                type="button"
                onClick={() => setCreatedQuiz({ id: 55, title: "Weekly Graphs Challenge" })}
                className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-black"
              >
                Create Quiz Record
              </button>
            </div>
          </Card>

          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Question Type</p>
                <h3 className="mt-2 text-2xl font-bold">Step 2: choose builder mode</h3>
              </div>
              {selectedQuestionType === "mcq" ? <SquareCheckBig className="h-5 w-5 text-accent" /> : <Code2 className="h-5 w-5 text-accent" />}
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <button
                type="button"
                onClick={() => setSelectedQuestionType("mcq")}
                className={selectedQuestionType === "mcq" ? "rounded-2xl border border-accent/30 bg-accent px-4 py-4 text-left text-sm font-semibold text-black" : "rounded-2xl border border-border bg-black/20 px-4 py-4 text-left text-sm font-semibold text-zinc-200"}
              >
                MCQ
                <p className={selectedQuestionType === "mcq" ? "mt-1 text-xs text-black/70" : "mt-1 text-xs text-zinc-500"}>Question, options, correct answer</p>
              </button>
              <button
                type="button"
                onClick={() => setSelectedQuestionType("coding")}
                className={selectedQuestionType === "coding" ? "rounded-2xl border border-accent/30 bg-accent px-4 py-4 text-left text-sm font-semibold text-black" : "rounded-2xl border border-border bg-black/20 px-4 py-4 text-left text-sm font-semibold text-zinc-200"}
              >
                Coding
                <p className={selectedQuestionType === "coding" ? "mt-1 text-xs text-black/70" : "mt-1 text-xs text-zinc-500"}>Prompt, samples, testcases, language control</p>
              </button>
            </div>
            <div className="mt-5 rounded-2xl border border-border bg-black/20 p-4 text-sm text-zinc-300">
              <p className="font-semibold text-foreground">Question storage</p>
              <p className="mt-2 text-zinc-400">All newly created questions are stored in the database and can be reused across multiple quizzes through the reusable question bank below.</p>
            </div>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Question Builder</p>
                <h3 className="mt-2 text-2xl font-bold">Step 3: create a new {selectedQuestionType.toUpperCase()}</h3>
              </div>
              {selectedQuestionType === "mcq" ? <SquareCheckBig className="h-5 w-5 text-accent" /> : <Code2 className="h-5 w-5 text-accent" />}
            </div>

            {selectedQuestionType === "mcq" ? (
              <div className="grid gap-4">
                <textarea className="min-h-[130px] rounded-3xl border border-border bg-black/30 p-4" placeholder="Enter MCQ question" />
                <div className="grid gap-3 md:grid-cols-2">
                  {["Option A", "Option B", "Option C", "Option D"].map((label) => (
                    <input key={label} className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder={label} />
                  ))}
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="Correct answer" />
                  <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="Topic" />
                </div>
              </div>
            ) : (
              <div className="grid gap-4">
                <textarea className="min-h-[130px] rounded-3xl border border-border bg-black/30 p-4" placeholder="Enter coding question prompt" />
                <div className="grid gap-3 md:grid-cols-2">
                  <textarea className="min-h-[110px] rounded-3xl border border-border bg-black/30 p-4" placeholder="Sample input" />
                  <textarea className="min-h-[110px] rounded-3xl border border-border bg-black/30 p-4" placeholder="Sample output" />
                </div>
                <textarea className="min-h-[120px] rounded-3xl border border-border bg-black/30 p-4" placeholder="Testcases JSON or structured input/output pairs" />
                <input className="h-12 rounded-2xl border border-border bg-black/30 px-4" placeholder="Topic" />
                <div>
                  <p className="mb-3 text-sm font-semibold text-foreground">Supported languages</p>
                  <div className="flex flex-wrap gap-2">
                    {codingLanguageOptions.map((language) => (
                      <button
                        key={language}
                        type="button"
                        onClick={() => toggleLanguage(language)}
                        className={selectedLanguages.includes(language) ? "rounded-full border border-accent/30 bg-accent px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-black" : "rounded-full border border-border px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-zinc-300"}
                      >
                        {language}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div className="mt-5 flex justify-end">
              <button type="button" className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-black">
                Save {selectedQuestionType === "mcq" ? "MCQ" : "Coding Question"}
              </button>
            </div>
          </Card>

          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Reusable Question Bank</p>
                <h3 className="mt-2 text-2xl font-bold">Step 4: attach existing questions</h3>
              </div>
              <Database className="h-5 w-5 text-accent" />
            </div>
            <div className="space-y-3">
              {reusableQuestions.map((question) => {
                const selected = attachedQuestionIds.includes(question.id);
                return (
                  <button
                    key={question.id}
                    type="button"
                    onClick={() => toggleAttachedQuestion(question.id)}
                    className={selected ? "w-full rounded-2xl border border-accent/30 bg-accent/10 p-4 text-left" : "w-full rounded-2xl border border-border bg-black/20 p-4 text-left hover:border-accent/30"}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-accent">{question.type}</p>
                        <p className="mt-2 font-semibold text-foreground">{question.question}</p>
                        <p className="mt-2 text-sm text-zinc-500">Topic: {question.topic}</p>
                        {question.options ? <p className="mt-1 text-xs text-zinc-500">Options: {question.options.join(" / ")}</p> : null}
                        {question.languages ? <p className="mt-1 text-xs text-zinc-500">Languages: {question.languages.join(", ")}</p> : null}
                      </div>
                      <span className={selected ? "rounded-full border border-accent/30 bg-accent px-3 py-2 text-xs font-bold uppercase tracking-[0.18em] text-black" : "rounded-full border border-border px-3 py-2 text-xs font-bold uppercase tracking-[0.18em] text-zinc-300"}>
                        {selected ? "Attached" : "Reuse"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
            <div className="mt-5 rounded-2xl border border-border bg-black/20 p-4">
              <p className="text-sm font-semibold text-foreground">Selected for current quiz</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {attachedQuestionIds.map((id) => (
                  <span key={id} className="rounded-full border border-accent/30 bg-accent/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-accent">
                    Question #{id}
                  </span>
                ))}
              </div>
              <button type="button" className="mt-4 rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-black">
                Attach to Quiz #{createdQuiz?.id ?? "--"}
              </button>
            </div>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Submission Trend</p>
                <h3 className="mt-2 text-2xl font-bold">Weekly platform throughput</h3>
              </div>
              <BarChart3 className="h-5 w-5 text-accent" />
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={adminStats.submissionsTrend}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                  <XAxis dataKey="label" stroke="#a1a1aa" />
                  <YAxis stroke="#a1a1aa" />
                  <Tooltip cursor={{ fill: "rgba(245,158,11,0.08)" }} />
                  <Bar dataKey="value" radius={[10, 10, 0, 0]} fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Platform Mix</p>
                <h3 className="mt-2 text-2xl font-bold">Core module distribution</h3>
              </div>
              <Database className="h-5 w-5 text-accent" />
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={adminStats.moduleDistribution} dataKey="value" nameKey="label" innerRadius={60} outerRadius={98} paddingAngle={3}>
                    {adminStats.moduleDistribution.map((entry, index) => (
                      <Cell key={entry.label} fill={pieColors[index % pieColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1fr_0.8fr]">
          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">Leaderboard</p>
                <h3 className="mt-2 text-2xl font-bold">Top users this cycle</h3>
              </div>
              <Trophy className="h-5 w-5 text-accent" />
            </div>
            <div className="space-y-3">
              {adminStats.topUsers.map((user, index) => (
                <div key={user.name} className="flex items-center justify-between rounded-2xl border border-border bg-black/20 px-4 py-4">
                  <div className="flex items-center gap-4">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full border border-accent/30 bg-accent/10 font-bold text-accent">
                      {index + 1}
                    </span>
                    <div>
                      <p className="font-semibold text-foreground">{user.name}</p>
                      <p className="text-sm text-zinc-500">{user.solved} solved</p>
                    </div>
                  </div>
                  <span className="text-lg font-bold text-accent">{user.score}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-accent">System Stats</p>
                <h3 className="mt-2 text-2xl font-bold">Operational health</h3>
              </div>
              <Activity className="h-5 w-5 text-accent" />
            </div>
            <div className="space-y-3">
              {adminStats.systemStats.map((item) => (
                <div key={item.label} className="rounded-2xl border border-border bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">{item.label}</p>
                  <p className="mt-2 text-2xl font-bold text-foreground">{item.value}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </section>
    </main>
  );
}
