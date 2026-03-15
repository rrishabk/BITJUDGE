import { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-12 w-full rounded-2xl border border-border bg-black/30 px-4 text-sm text-foreground outline-none ring-0 placeholder:text-zinc-500 focus:border-accent",
        className,
      )}
      {...props}
    />
  );
}
