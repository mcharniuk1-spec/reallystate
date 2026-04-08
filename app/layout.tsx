import type { Metadata } from "next";
import { Newsreader, Outfit } from "next/font/google";

import { Providers } from "./providers";
import { ChatBar } from "@/components/chat/ChatBar";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const newsreader = Newsreader({
  subsets: ["latin"],
  variable: "--font-newsreader",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "BGEstate — Every property in Bulgaria",
    template: "%s · BGEstate",
  },
  description: "Every property. One search. 3D map. AI-powered Bulgarian real estate marketplace.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${outfit.variable} ${newsreader.variable}`}>
      <body className="font-sans pb-[52px]">
        <Providers>
          {children}
          <ChatBar />
        </Providers>
      </body>
    </html>
  );
}
