import Link from "next/link";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/shell/AppShell";

type Props = { params: Promise<{ id: string }> };

export default async function PropertyDetailPage({ params }: Props) {
  const { id } = await params;
  if (!id) notFound();

  const isPreview = id.startsWith("preview-");

  return (
    <AppShell
      title={isPreview ? "Property shell (preview)" : "Property"}
      subtitle="Deduped property view with gallery, facts, contacts, and source provenance will load from `/properties/{id}` APIs."
    >
      <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="aspect-[4/3] rounded-3xl border border-line bg-gradient-to-br from-paper to-panel shadow-inner flex items-center justify-center">
          <p className="text-mist text-sm px-6 text-center">Photo gallery placeholder — media pipeline hooks here</p>
        </div>
        <div className="space-y-6">
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
            <p className="text-xs uppercase tracking-wide text-mist">Canonical ID</p>
            <p className="mt-1 font-mono text-lg text-ink break-all">{id}</p>
          </div>
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
            <p className="text-xs uppercase tracking-wide text-mist">Price & facts</p>
            <p className="mt-3 text-mist text-sm leading-relaxed">
              Price box, rooms, area, and Act 16 fields will render from normalized offers once persistence is wired.
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/listings"
              className="inline-flex flex-1 justify-center rounded-full border border-line px-4 py-2.5 text-sm font-semibold text-ink hover:border-sea/40"
            >
              Back to listings
            </Link>
            <button
              type="button"
              className="inline-flex flex-1 justify-center rounded-full bg-sea px-4 py-2.5 text-sm font-semibold text-white hover:bg-sea-bright cursor-not-allowed opacity-70"
              disabled
              title="CRM lead action — needs `/crm` APIs"
            >
              Create lead
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
