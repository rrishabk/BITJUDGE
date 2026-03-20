"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { Card } from "@/components/ui/card";
import { practiceProblems as initialProblems } from "@/lib/mock-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "/api/v1";

type PracticeProblem = {
  id?: number;
  title: string;
  platform: string;
  link: string;
  difficulty: number;
  topic: string;
  solved: boolean;
};

export default function PracticePage() {
  const [problems, setProblems] = useState<PracticeProblem[]>(
    initialProblems.map((problem, index) => ({ ...problem, id: index + 1 })),
  );
  const [selectedTopic, setSelectedTopic] = useState<string>("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("all");
  const [selectedPlatform, setSelectedPlatform] = useState<string>("all");

  const topics = useMemo(
    () => ["all", ...Array.from(new Set(problems.map((problem) => problem.topic)))],
    [problems],
  );
  const difficulties = useMemo(
    () => ["all", ...Array.from(new Set(problems.map((problem) => String(problem.difficulty))))],
    [problems],
  );
  const platforms = useMemo(
    () => ["all", ...Array.from(new Set(problems.map((problem) => problem.platform)))],
    [problems],
  );

  const filteredProblems = useMemo(() => {
    return problems.filter((problem) => {
      const matchesTopic = selectedTopic === "all" || problem.topic === selectedTopic;
      const matchesDifficulty = selectedDifficulty === "all" || String(problem.difficulty) === selectedDifficulty;
      const matchesPlatform = selectedPlatform === "all" || problem.platform === selectedPlatform;
      return matchesTopic && matchesDifficulty && matchesPlatform;
    });
  }, [problems, selectedDifficulty, selectedPlatform, selectedTopic]);

  const solvedCount = problems.filter((problem) => problem.solved).length;
  const totalCount = problems.length;
  const progressPercent = totalCount === 0 ? 0 : Math.round((solvedCount / totalCount) * 100);

  async function toggleSolved(problemId: number, solved: boolean) {
    setProblems((current) =>
      current.map((problem) => (problem.id === problemId ? { ...problem, solved } : problem)),
    );

    try {
      await fetch(`${API_URL}/problems/mark-solved`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ problem_id: problemId, solved }),
      });
    } catch {
      // Keep optimistic UI for scaffold mode when backend is unavailable.
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.4em] text-accent">Practice</p>
          <h1 className="mt-2 text-4xl font-black">Problem board</h1>
          <p className="mt-3 max-w-2xl text-sm text-zinc-400">
            Filter by topic, difficulty, and platform. Track solved status and move through the set like a proper coding grindboard.
          </p>
        </div>
        <div className="min-w-[280px] rounded-[28px] border border-accent/20 bg-[#14100b] p-5 shadow-glow">
          <div className="flex items-center justify-between text-sm font-semibold text-zinc-300">
            <span>Progress</span>
            <span className="text-accent">{solvedCount} / {totalCount}</span>
          </div>
          <div className="mt-3 h-3 overflow-hidden rounded-full bg-black/40">
            <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${progressPercent}%` }} />
          </div>
          <p className="mt-3 text-xs uppercase tracking-[0.24em] text-zinc-500">Solved / Total problems</p>
        </div>
      </div>

      <Card className="mb-6">
        <div className="grid gap-4 lg:grid-cols-3">
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Topic</span>
            <select
              value={selectedTopic}
              onChange={(event) => setSelectedTopic(event.target.value)}
              className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4 text-sm text-foreground outline-none"
            >
              {topics.map((topic) => (
                <option key={topic} value={topic} className="bg-[#101010]">
                  {topic}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Difficulty</span>
            <select
              value={selectedDifficulty}
              onChange={(event) => setSelectedDifficulty(event.target.value)}
              className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4 text-sm text-foreground outline-none"
            >
              {difficulties.map((difficulty) => (
                <option key={difficulty} value={difficulty} className="bg-[#101010]">
                  {difficulty}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2 text-sm text-zinc-300">
            <span>Platform</span>
            <select
              value={selectedPlatform}
              onChange={(event) => setSelectedPlatform(event.target.value)}
              className="h-12 w-full rounded-2xl border border-border bg-black/30 px-4 text-sm text-foreground outline-none"
            >
              {platforms.map((platform) => (
                <option key={platform} value={platform} className="bg-[#101010]">
                  {platform}
                </option>
              ))}
            </select>
          </label>
        </div>
      </Card>

      <Card className="overflow-hidden p-0">
        <div className="grid grid-cols-[72px_minmax(240px,1.7fr)_120px_160px_140px_140px] border-b border-border bg-[#141414] px-6 py-4 text-xs font-semibold uppercase tracking-[0.24em] text-zinc-500">
          <span>Done</span>
          <span>Problem Title</span>
          <span>Difficulty</span>
          <span>Topic</span>
          <span>Platform</span>
          <span>Action</span>
        </div>
        <div>
          {filteredProblems.map((problem) => (
            <div
              key={problem.title}
              className="grid grid-cols-[72px_minmax(240px,1.7fr)_120px_160px_140px_140px] items-center border-b border-border/80 px-6 py-4 transition hover:bg-[#141414]"
            >
              <div>
                <input
                  type="checkbox"
                  checked={problem.solved}
                  onChange={(event) => toggleSolved(problem.id ?? 0, event.target.checked)}
                  className="h-5 w-5 rounded border-border accent-orange-500"
                />
              </div>
              <div className="pr-4">
                <p className="font-semibold text-foreground">{problem.title}</p>
              </div>
              <div>
                <span className="rounded-full border border-accent/20 bg-accent/10 px-3 py-2 text-xs font-semibold text-accent">
                  {problem.difficulty}
                </span>
              </div>
              <div>
                <span className="text-sm text-zinc-300">{problem.topic}</span>
              </div>
              <div>
                <span className="text-sm text-zinc-300">{problem.platform}</span>
              </div>
              <div>
                <Link
                  href={problem.link}
                  className="inline-flex rounded-2xl border border-accent/30 px-4 py-2 text-sm font-semibold text-accent transition hover:bg-accent hover:text-black"
                >
                  Solve
                </Link>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </main>
  );
}
