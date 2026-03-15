"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const allowedDomain = "@juetguna.in";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email.toLowerCase().endsWith(allowedDomain)) {
      setError("Only JUET students can login.");
      return;
    }
    if (!password.trim()) {
      setError("Password is required.");
      return;
    }

    setError("");
    document.cookie = `bitjudge_token=demo-session; path=/; max-age=${60 * 60 * 24}; samesite=lax`;
    router.push("/dashboard");
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-80px)] max-w-6xl items-center px-6 py-12">
      <Card className="mx-auto grid w-full max-w-5xl gap-8 overflow-hidden p-0 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="grid-surface bg-black/50 p-8 lg:p-12">
          <p className="text-xs uppercase tracking-[0.38em] text-accent">Powered by BITWISE</p>
          <h1 className="mt-4 text-5xl font-black tracking-[0.16em] text-foreground">BITJUDGE</h1>
          <p className="mt-6 max-w-lg text-lg text-zinc-300">
            Login using your JUET college email.
          </p>
        </div>
        <form className="space-y-4 p-8 lg:p-12" onSubmit={handleSubmit}>
          <h2 className="text-2xl font-semibold text-foreground">Login</h2>
          <label className="block space-y-2 text-sm text-zinc-300">
            <span>Email</span>
            <Input
              type="email"
              placeholder="name@juetguna.in"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="block space-y-2 text-sm text-zinc-300">
            <span>Password</span>
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error ? <p className="text-sm font-medium text-red-400">{error}</p> : null}
          <Button className="w-full bg-accent text-black" type="submit">Login</Button>
        </form>
      </Card>
    </main>
  );
}
