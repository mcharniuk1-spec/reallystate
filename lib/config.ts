/** Base URL for the Python dev API (`make run-api`). Server-side only unless proxied. */
export function getApiBaseUrl(): string {
  const raw = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
  return raw.replace(/\/$/, "");
}
