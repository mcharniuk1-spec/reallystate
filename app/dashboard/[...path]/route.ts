import { readFile } from "fs/promises";
import path from "path";
import { NextRequest, NextResponse } from "next/server";

const REPO_ROOT = process.cwd();
const DASHBOARD_ROOT = path.join(REPO_ROOT, "docs", "dashboard");

const CONTENT_TYPES: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
};

type Params = { path?: string[] };

export async function GET(_request: NextRequest, context: { params: Promise<Params> }) {
  const params = await context.params;
  const parts = params.path?.length ? params.path : ["index.html"];
  const requested = path.normalize(path.join(DASHBOARD_ROOT, ...parts));

  if (!requested.startsWith(DASHBOARD_ROOT)) {
    return NextResponse.json({ error: "invalid_dashboard_path" }, { status: 400 });
  }

  try {
    const data = await readFile(requested);
    const ext = path.extname(requested).toLowerCase();
    return new NextResponse(data, {
      headers: {
        "Content-Type": CONTENT_TYPES[ext] ?? "application/octet-stream",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json({ error: "dashboard_not_found" }, { status: 404 });
  }
}
