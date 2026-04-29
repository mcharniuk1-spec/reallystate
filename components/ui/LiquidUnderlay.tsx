"use client";

import { motion } from "framer-motion";

/**
 * Subtle animated gradient + glass shimmer behind page content.
 * Keeps pointer-events off so map/list interactions stay unaffected.
 */
export function LiquidUnderlay() {
  return (
    <div
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      aria-hidden
    >
      <motion.div
        className="absolute -inset-[35%] opacity-55 blur-3xl"
        style={{
          background:
            "conic-gradient(from 120deg at 30% 40%, rgb(13 138 114 / 0.35), rgb(201 169 98 / 0.22), rgb(11 107 87 / 0.28), rgb(52 211 153 / 0.18), rgb(13 138 114 / 0.35))",
        }}
        animate={{ rotate: [0, 8, -6, 0], scale: [1, 1.04, 1] }}
        transition={{ duration: 28, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_55%_at_50%_-10%,rgb(13_138_114/0.12),transparent_55%)] dark:bg-[radial-gradient(ellipse_90%_55%_at_50%_-10%,rgb(52_211_153/0.14),transparent_55%)]" />
      <motion.div
        className="absolute inset-0 mix-blend-soft-light opacity-30"
        style={{
          background:
            "linear-gradient(115deg, transparent 40%, rgb(255 255 255 / 0.35) 50%, transparent 60%)",
        }}
        animate={{ x: ["-30%", "40%"] }}
        transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}
