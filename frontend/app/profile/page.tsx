"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { studentStats } from "@/lib/mock-data";

export default function ProfilePage() {
  const [handles, setHandles] = useState(studentStats.handles);

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.4em] text-accent">Profile</p>
        <h1 className="mt-2 text-4xl font-black">Edit competitive programming handles</h1>
      </div>
      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          {Object.entries(handles).map(([key, value]) => (
            <label key={key} className="space-y-2 text-sm text-zinc-300">
              <span className="capitalize">{key.replace("leetcode", "LeetCode").replace("codeforces", "Codeforces").replace("codechef", "CodeChef").replace("hackerrank", "HackerRank").replace("github", "GitHub")}</span>
              <Input
                value={value}
                onChange={(event) => setHandles((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-6 flex justify-end">
          <Button>Save Handles</Button>
        </div>
      </Card>
    </main>
  );
}
