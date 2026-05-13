"use client";

import { useMemo, useState } from "react";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const THREADS = [
  { id: "search", title: "Bulgaria search", kind: "AI", propertyId: null },
  { id: "property-demo-001", title: "Liked apartment", kind: "Property", propertyId: "demo-001" },
  { id: "property-demo-004", title: "Viewing plan", kind: "Property", propertyId: "demo-004" },
];

const SEED: Record<string, Message[]> = {
  search: [
    {
      id: "a0",
      role: "assistant",
      content: "Tell me the location, budget, and must-have facts. I will keep missing evidence explicit.",
    },
  ],
  "property-demo-001": [
    {
      id: "a1",
      role: "assistant",
      content: "This chat is linked to a liked property thread.",
    },
  ],
  "property-demo-004": [
    {
      id: "a2",
      role: "assistant",
      content: "Ask about source evidence, photos, price, or viewing steps.",
    },
  ],
};

export function ChatWorkspace() {
  const [activeThread, setActiveThread] = useState(THREADS[0].id);
  const [messagesByThread, setMessagesByThread] = useState<Record<string, Message[]>>(SEED);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState("local");

  const thread = useMemo(
    () => THREADS.find((item) => item.id === activeThread) ?? THREADS[0],
    [activeThread],
  );
  const messages = messagesByThread[thread.id] ?? [];

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setLoading(true);
    const userMessage: Message = { id: `u-${Date.now()}`, role: "user", content: text };
    const next = [...messages, userMessage];
    setMessagesByThread((prev) => ({ ...prev, [thread.id]: next }));

    try {
      const res = await fetch("/api/backend/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          property_id: thread.propertyId,
          active_filters: { surface: "chat_page", thread: thread.kind },
          selected_property: thread.propertyId ? { property_id: thread.propertyId, state: "liked" } : {},
          messages: [
            {
              role: "system",
              content:
                "You are a Bulgaria real-estate assistant. Use source evidence, property context, and map/filter context. Do not invent missing details.",
            },
            ...next.map((msg) => ({ role: msg.role, content: msg.content })),
          ],
        }),
      });
      const data = (await res.json()) as { message?: string; provider?: string; error?: string };
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`);
      setProvider(data.provider ?? "api");
      setMessagesByThread((prev) => ({
        ...prev,
        [thread.id]: [
          ...(prev[thread.id] ?? []),
          { id: `a-${Date.now()}`, role: "assistant", content: data.message ?? "" },
        ],
      }));
    } catch (error) {
      setProvider("fallback");
      setMessagesByThread((prev) => ({
        ...prev,
        [thread.id]: [
          ...(prev[thread.id] ?? []),
          {
            id: `e-${Date.now()}`,
            role: "assistant",
            content: error instanceof Error ? error.message : "Chat request failed",
          },
        ],
      }));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
      <aside className="rounded-xl border border-line bg-panel p-2">
        {THREADS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setActiveThread(item.id)}
            className={`mb-1 w-full rounded-lg px-3 py-3 text-left transition-colors ${
              item.id === thread.id ? "bg-sea/10 text-sea" : "text-ink hover:bg-paper"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-semibold">{item.title}</span>
              <span className="rounded-full bg-paper px-2 py-0.5 text-[10px] text-mist">{item.kind}</span>
            </div>
            <p className="mt-1 truncate text-xs text-mist">
              {item.propertyId ? `Property ${item.propertyId}` : "Search assistant"}
            </p>
          </button>
        ))}
      </aside>

      <section className="flex min-h-[560px] flex-col rounded-xl border border-line bg-panel shadow-lift">
        <div className="border-b border-line px-5 py-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-ink">{thread.title}</h2>
              <p className="text-xs text-mist">{thread.kind} · {provider}</p>
            </div>
            {thread.propertyId ? (
              <span className="rounded-full bg-sand/15 px-3 py-1 text-xs font-semibold text-sand">
                Liked
              </span>
            ) : null}
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto p-5">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[82%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  message.role === "user"
                    ? "rounded-tr-md bg-sea text-white"
                    : "rounded-tl-md border border-line bg-paper text-ink"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-line p-4">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void send();
                }
              }}
              disabled={loading}
              className="h-11 flex-1 rounded-xl border border-line bg-paper px-4 text-sm text-ink outline-none focus:border-sea/40"
              placeholder={thread.propertyId ? "Ask about this property" : "Ask about the market"}
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={!input.trim() || loading}
              className="h-11 rounded-xl bg-ink px-4 text-sm font-semibold text-paper disabled:opacity-40"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
