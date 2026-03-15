import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-3xl border border-border bg-panel/90 p-6 shadow-glow backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}
