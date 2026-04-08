import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f1419",
        mist: "#64748b",
        paper: "#f6f3ed",
        panel: "#fffcf7",
        line: "#e5dfd3",
        sea: "#0b6b57",
        "sea-bright": "#0d8a72",
        sand: "#c9a962",
        warn: "#b45309",
      },
      fontFamily: {
        sans: ["var(--font-outfit)", "system-ui", "sans-serif"],
        display: ["var(--font-newsreader)", "Georgia", "serif"],
      },
      boxShadow: {
        lift: "0 18px 50px rgb(15 20 25 / 8%)",
      },
    },
  },
  plugins: [],
};

export default config;
