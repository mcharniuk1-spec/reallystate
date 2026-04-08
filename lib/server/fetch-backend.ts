import { getApiBaseUrl } from "@/lib/config";
import type { DevHealth, SourcesPayload } from "@/lib/types/api";

export type BackendResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; status?: number };

async function readJson<T>(path: string): Promise<BackendResult<T>> {
  const base = getApiBaseUrl();
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;
  try {
    const res = await fetch(url, { cache: "no-store", next: { revalidate: 0 } });
    if (!res.ok) {
      return { ok: false, error: `HTTP ${res.status}`, status: res.status };
    }
    return { ok: true, data: (await res.json()) as T };
  } catch {
    return { ok: false, error: "Could not reach the dev API. Run `make run-api`." };
  }
}

export function fetchDevHealth(): Promise<BackendResult<DevHealth>> {
  return readJson<DevHealth>("/health");
}

export function fetchSources(): Promise<BackendResult<SourcesPayload>> {
  return readJson<SourcesPayload>("/sources");
}
