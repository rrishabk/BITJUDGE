import Link from "next/link";

import { Button } from "@/components/ui/button";

export function LandingHero() {
  return (
    <section className="grid-surface relative overflow-hidden">
      <div className="mx-auto flex min-h-[calc(100vh-80px)] max-w-7xl flex-col justify-center gap-10 px-6 py-16 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-3xl space-y-6">
          <p className="text-sm uppercase tracking-[0.5em] text-accent">Professional Coding Platform</p>
          <h1 className="text-5xl font-black uppercase leading-none sm:text-7xl">
            Orange-black competitive coding for BIT students.
          </h1>
          <p className="max-w-2xl text-lg text-zinc-300">
            Run quizzes, code with Judge0, track topic weakness, and manage practice progress from one responsive platform.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link href="/login"><Button>Login With College Email</Button></Link>
            <Link href="/dashboard"><Button className="bg-zinc-100 text-black">Open Dashboard</Button></Link>
          </div>
        </div>
      </div>
    </section>
  );
}
