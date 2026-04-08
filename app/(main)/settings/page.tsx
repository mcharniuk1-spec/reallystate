import { AppShell } from "@/components/shell/AppShell";

const rows = [
  { label: "Profile", hint: "Name, locale, notifications" },
  { label: "Team & roles", hint: "RBAC from `/settings/team`" },
  { label: "API keys", hint: "Automation keys with audit" },
  { label: "Connected channels", hint: "WhatsApp, email, portal accounts" },
  { label: "Publishing", hint: "Distribution profiles and dry-runs" },
];

export default function SettingsPage() {
  return (
    <AppShell
      title="Settings"
      subtitle="Operator and team controls. Forms stay disabled until auth and settings APIs are implemented."
    >
      <ul className="divide-y divide-line rounded-2xl border border-line bg-panel shadow-lift overflow-hidden">
        {rows.map((row) => (
          <li key={row.label} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 px-6 py-4">
            <div>
              <p className="font-semibold text-ink">{row.label}</p>
              <p className="text-sm text-mist">{row.hint}</p>
            </div>
            <button
              type="button"
              disabled
              className="shrink-0 rounded-full border border-line px-4 py-2 text-xs font-semibold text-mist cursor-not-allowed"
            >
              Soon
            </button>
          </li>
        ))}
      </ul>
    </AppShell>
  );
}
