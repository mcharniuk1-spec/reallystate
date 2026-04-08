"use client";

import { useState, useRef, useEffect } from "react";

type ChatTab = "search" | "property";

type Message = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
};

const DEMO_SEARCH_MESSAGES: Message[] = [
  { id: "s1", role: "assistant", content: "Hi! I can help you find properties in Bulgaria. Try asking me about apartments, price ranges, or neighborhoods.", timestamp: new Date() },
];

const DEMO_PROPERTY_MESSAGES: Message[] = [
  { id: "p1", role: "system", content: "Property chats will connect you with owners and representatives. This feature requires the CRM backend.", timestamp: new Date() },
];

function ChatMessage({ msg }: { msg: Message }) {
  return (
    <div
      className={`flex gap-2.5 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
    >
      <div
        className={`shrink-0 mt-0.5 h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
          msg.role === "user"
            ? "bg-sea text-white"
            : msg.role === "assistant"
              ? "bg-gradient-to-br from-sea to-sea-bright text-white"
              : "bg-mist/20 text-mist"
        }`}
      >
        {msg.role === "user" ? "U" : msg.role === "assistant" ? "AI" : "i"}
      </div>
      <div
        className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
          msg.role === "user"
            ? "bg-sea text-white rounded-tr-md"
            : msg.role === "assistant"
              ? "bg-panel border border-line text-ink rounded-tl-md"
              : "bg-paper border border-line/50 text-mist text-xs italic rounded-tl-md"
        }`}
      >
        {msg.content}
      </div>
    </div>
  );
}

export function ChatBar() {
  const [expanded, setExpanded] = useState(false);
  const [tab, setTab] = useState<ChatTab>("search");
  const [input, setInput] = useState("");
  const [searchMsgs, setSearchMsgs] = useState<Message[]>(DEMO_SEARCH_MESSAGES);
  const [propertyMsgs] = useState<Message[]>(DEMO_PROPERTY_MESSAGES);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const messages = tab === "search" ? searchMsgs : propertyMsgs;

  useEffect(() => {
    if (expanded) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages.length, expanded]);

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    setInput("");

    if (tab === "search") {
      const userMsg: Message = {
        id: `u-${Date.now()}`,
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      setSearchMsgs((prev) => [...prev, userMsg]);

      setTimeout(() => {
        const aiMsg: Message = {
          id: `a-${Date.now()}`,
          role: "assistant",
          content: getAIResponse(text),
          timestamp: new Date(),
        };
        setSearchMsgs((prev) => [...prev, aiMsg]);
      }, 600);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 transition-all duration-300 ease-out ${
        expanded ? "h-[420px] sm:h-[480px]" : "h-auto"
      }`}
    >
      {/* Backdrop when expanded */}
      {expanded && (
        <div
          className="fixed inset-0 bg-ink/10 -z-10"
          onClick={() => setExpanded(false)}
        />
      )}

      <div className="h-full flex flex-col bg-panel border-t border-line shadow-[0_-8px_30px_rgba(0,0,0,0.08)]">
        {/* Tab bar + controls */}
        <div className="shrink-0 flex items-center justify-between gap-3 px-4 py-2 border-b border-line/50">
          {/* Tabs */}
          <div className="flex gap-1 rounded-lg bg-paper p-0.5 border border-line/50">
            <button
              type="button"
              onClick={() => setTab("search")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                tab === "search"
                  ? "bg-sea text-white shadow-sm"
                  : "text-mist hover:text-ink"
              }`}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              Search chats
            </button>
            <button
              type="button"
              onClick={() => setTab("property")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                tab === "property"
                  ? "bg-sea text-white shadow-sm"
                  : "text-mist hover:text-ink"
              }`}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
              Property chats
              <span className="flex h-4 min-w-[16px] items-center justify-center rounded-full bg-sand/20 text-sand text-[9px] font-bold px-1">
                0
              </span>
            </button>
          </div>

          {/* Expand / collapse */}
          <div className="flex items-center gap-1.5">
            {expanded && (
              <span className="text-[10px] text-mist hidden sm:inline">
                {tab === "search" ? "AI assistant" : "Owner messages"}
              </span>
            )}
            <button
              type="button"
              onClick={() => setExpanded(!expanded)}
              className="flex items-center justify-center h-7 w-7 rounded-lg text-mist hover:text-ink hover:bg-paper transition-colors"
              title={expanded ? "Minimize chat" : "Expand chat"}
            >
              {expanded ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="4 14 10 14 10 20" />
                  <polyline points="20 10 14 10 14 4" />
                  <line x1="14" y1="10" x2="21" y2="3" />
                  <line x1="3" y1="21" x2="10" y2="14" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 3 21 3 21 9" />
                  <polyline points="9 21 3 21 3 15" />
                  <line x1="21" y1="3" x2="14" y2="10" />
                  <line x1="3" y1="21" x2="10" y2="14" />
                </svg>
              )}
            </button>
            {expanded && (
              <button
                type="button"
                onClick={() => setExpanded(false)}
                className="flex items-center justify-center h-7 w-7 rounded-lg text-mist hover:text-ink hover:bg-paper transition-colors"
                title="Close"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Messages area (only visible when expanded) */}
        {expanded && (
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} msg={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input bar (always visible) */}
        <div className="shrink-0 px-4 py-2.5 border-t border-line/30">
          <div className="flex items-center gap-2 max-w-4xl mx-auto">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => { if (!expanded) setExpanded(true); }}
                placeholder={
                  tab === "search"
                    ? "Ask AI: \"Find 2-bed apartments in Varna under €90K\"..."
                    : "Message property owner..."
                }
                className="w-full rounded-xl border border-line bg-paper pl-4 pr-10 py-2 text-sm text-ink placeholder:text-mist/40 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20"
              />
              <button
                type="button"
                onClick={handleSend}
                disabled={!input.trim()}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 flex h-7 w-7 items-center justify-center rounded-lg bg-sea text-white disabled:opacity-30 hover:bg-sea-bright transition-colors"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getAIResponse(query: string): string {
  const q = query.toLowerCase();
  if (q.includes("varna") && q.includes("apartment")) {
    return "I found several apartments in Varna! The Sea Garden district has studios from €450/mo, while Chaika has 2-bed apartments starting at €85K for sale. Would you like me to filter the map to show these?";
  }
  if (q.includes("price") || q.includes("cheap") || q.includes("afford")) {
    return "For the best value in Bulgaria, check Burgas coast — Sarafovo has 2-bed apartments from €89K with sea views. In Varna, Mladost district offers apartments under €80K. Shall I show you these on the map?";
  }
  if (q.includes("invest") || q.includes("yield") || q.includes("str") || q.includes("rental")) {
    return "Great question! Varna's gross STR yield averages 4.08% with €14,200 annual revenue per listing. Occupancy is 59% with €65 ADR. Burgas offers slightly higher yields at 4.57%. I can pull detailed analytics once our AirDNA integration is live.";
  }
  if (q.includes("house") || q.includes("villa")) {
    return "I see houses and villas across Bulgaria. Bansko has mountain houses from €295K, while Sozopol has luxury villas with sea views from €340K. What area and budget are you considering?";
  }
  return `I understand you're looking for "${query}". The AI search backend is being connected — for now I can help with general Bulgaria real estate questions. Try asking about specific cities, property types, or investment yields!`;
}
