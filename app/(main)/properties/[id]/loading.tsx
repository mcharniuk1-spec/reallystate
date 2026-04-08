import { PropertyDetailSkeleton } from "@/components/listings/ListingSkeleton";
import { SiteHeader } from "@/components/shell/SiteHeader";

export default function PropertyLoading() {
  return (
    <div className="min-h-screen flex flex-col bg-paper">
      <SiteHeader />
      <PropertyDetailSkeleton />
    </div>
  );
}
