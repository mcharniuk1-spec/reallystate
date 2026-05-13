import type { Metadata } from "next";

import { AccountCabinet } from "@/components/account/AccountCabinet";
import { SiteHeader } from "@/components/shell/SiteHeader";

export const metadata: Metadata = {
  title: "Profile · BGEstate",
};

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen flex-col bg-paper">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">
        <div className="mb-6">
          <h1 className="font-display text-2xl tracking-tight text-ink sm:text-3xl">Profile</h1>
          <p className="mt-1 text-sm text-mist">Account, liked properties, alerts, and mode settings</p>
        </div>
        <AccountCabinet />
      </main>
    </div>
  );
}
