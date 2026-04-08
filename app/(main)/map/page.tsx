import type { Metadata } from "next";

import { FullScreenMap } from "@/components/map/FullScreenMap";

export const metadata: Metadata = {
  title: "Map",
};

export default function MapPage() {
  return <FullScreenMap />;
}
