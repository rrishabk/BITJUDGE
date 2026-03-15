import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#000000",
        foreground: "#f5f5f5",
        panel: "#1A1A1A",
        accent: "#FF6B00",
        accentMuted: "#8a3b00",
        border: "rgba(255,255,255,0.08)",
      },
      boxShadow: {
        glow: "0 0 40px rgba(255, 107, 0, 0.18)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
