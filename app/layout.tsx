import type { Metadata } from "next";

import { Providers } from "./providers";
import { ChatBar } from "@/components/chat/ChatBar";
import { LiquidUnderlay } from "@/components/ui/LiquidUnderlay";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "BGEstate — Every property in Bulgaria",
    template: "%s · BGEstate",
  },
  description: "Every property. One search. 3D map. AI-powered Bulgarian real estate marketplace.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans pb-[52px]">
        <LiquidUnderlay />
        <Providers>
          {children}
          <ChatBar />
        </Providers>
      </body>
    </html>
  );
}
