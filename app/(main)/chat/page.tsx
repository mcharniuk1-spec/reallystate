import { AssistantPlayground } from "@/components/chat/AssistantPlayground";
import { AppShell } from "@/components/shell/AppShell";

export default function ChatPage() {
  return (
    <AppShell
      title="Chat inbox"
      subtitle="CRM threads will use lead_message APIs; the assistant below calls the Python FastAPI chat endpoint via the Next.js proxy."
    >
      <div className="grid gap-4 lg:grid-cols-[280px_1fr] min-h-[420px]">
        <div className="rounded-2xl border border-line bg-panel p-4 shadow-lift">
          <p className="text-xs font-semibold uppercase tracking-wide text-mist">Threads</p>
          <p className="mt-8 text-sm text-mist">No threads yet — backend CRM slice pending.</p>
        </div>
        <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift flex flex-col">
          <p className="text-mist text-sm flex-1">
            Select a conversation to preview messages and linked properties (CRM APIs next).
          </p>
          <AssistantPlayground />
        </div>
      </div>
    </AppShell>
  );
}
