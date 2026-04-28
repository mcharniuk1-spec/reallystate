import { readFile } from "fs/promises";
import path from "path";
import type { Listing } from "@/lib/types/listing";

const DATA_PATH = path.join(process.cwd(), "public", "data", "scraped-listings.json");

export async function readScrapedListings(): Promise<Listing[]> {
  try {
    const raw = await readFile(DATA_PATH, "utf8");
    return JSON.parse(raw) as Listing[];
  } catch {
    return [];
  }
}

