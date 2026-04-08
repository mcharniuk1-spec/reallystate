import { AppShell } from "@/components/shell/AppShell";

const queues = [
  "Source health",
  "Parser failures",
  "Duplicate review",
  "Geocode review",
  "Compliance",
  "Publish jobs",
];

export default function AdminPage() {
  return (
    <AppShell
      title="Operator admin"
      subtitle="Review queues and crawl visibility stay behind auth. This layout reserves space for tables and filters from `/admin` APIs."
    >
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {queues.map((name) => (
          <div
            key={name}
            className="rounded-2xl border border-line bg-panel p-5 shadow-lift hover:border-sea/20 transition-colors"
          >
            <p className="font-display text-lg text-ink">{name}</p>
            <p className="mt-2 text-sm text-mist">Queue placeholder — connect operator API + RBAC.</p>
          </div>
        ))}
      </div>
    </AppShell>
  );
}
