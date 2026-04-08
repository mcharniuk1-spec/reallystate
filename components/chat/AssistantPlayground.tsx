"use client";

import { useState } from "react";

type ChatMessage = { role: "user" | "assistant"; content: string };

export function AssistantPlayground() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setError(null);
    setLoading(true);
    const next: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    try {
      const res = await fetch("/api/backend/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [
            {
              role: "system",
              content:
                "You help Bulgaria real estate operators with listings, CRM, and compliance. Be concise.",
            },
            ...next.map((m) => ({ role: m.role, content: m.content })),
          ],
        }),
      });
      const data = (await res.json()) as { message?: string; provider?: string; error?: string };
      if (!res.ok) {
        throw new Error(data.error ?? `HTTP ${res.status}`);
      }
      const assistantText = data.message ?? "";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: assistantText },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-3 border-t border-line pt-4 mt-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-mist">Assistant (backend)</p>
      <p className="text-xs text-mist">
        Proxied to Python FastAPI. Default is a local stub; set{" "}
        <code className="rounded bg-paper px-1">CHAT_PROVIDER=openai</code> and{" "}
        <code className="rounded bg-paper px-1">OPENAI_API_KEY</code> on the API process for live answers.
      </p>
      <div className="max-h-48 overflow-y-auto rounded-xl border border-line bg-paper p-3 text-sm space-y-2">
        {messages.length === 0 ? (
          <p className="text-mist">No messages yet.</p>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "text-ink" : "text-mist"}>
              <span className="font-semibold text-xs uppercase">{m.role}</span>
              <p className="whitespace-pre-wrap">{m.content}</p>
            </div>
          ))
        )}
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <div className="flex gap-2">
        <input
          className="flex-1 h-11 rounded-xl bg-paper border border-line text-sm px-4 text-ink"
          placeholder="Ask about listings, CRM, or ingestion…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
          disabled={loading}
        />
        <button
          type="button"
          onClick={() => void send()}
          disabled={loading || !input.trim()}
          className="h-11 px-4 rounded-xl bg-ink text-paper text-sm font-medium disabled:opacity-50"
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
