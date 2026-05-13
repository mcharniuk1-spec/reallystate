import type { Metadata } from "next";

import { ChatWorkspace } from "@/components/chat/ChatWorkspace";
import { SiteHeader } from "@/components/shell/SiteHeader";

export const metadata: Metadata = {
  title: "Chat · BGEstate",
};

export default function ChatPage() {
  return (
    <div className="flex min-h-screen flex-col bg-paper">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl tracking-tight text-ink sm:text-3xl">Chats</h1>
            <p className="mt-1 text-sm text-mist">Search threads and property conversations</p>
          </div>
        </div>
        <ChatWorkspace />
      </main>
    </div>
  );
}
