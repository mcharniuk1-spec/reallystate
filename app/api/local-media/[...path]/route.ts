import { readFile } from "fs/promises";
import path from "path";
import { NextRequest, NextResponse } from "next/server";

const REPO_ROOT = process.cwd();
const MEDIA_ROOT = path.join(REPO_ROOT, "data", "media");

const CONTENT_TYPES: Record<string, string> = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

type Params = { path?: string[] };

export async function GET(_request: NextRequest, context: { params: Promise<Params> }) {
  const params = await context.params;
  const parts = params.path ?? [];
  const requested = path.normalize(path.join(MEDIA_ROOT, ...parts));

  if (!requested.startsWith(MEDIA_ROOT)) {
    return NextResponse.json({ error: "invalid_media_path" }, { status: 400 });
  }

  try {
    const data = await readFile(requested);
    const ext = path.extname(requested).toLowerCase();
    return new NextResponse(data, {
      headers: {
        "Content-Type": CONTENT_TYPES[ext] ?? "application/octet-stream",
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch {
    return NextResponse.json({ error: "media_not_found" }, { status: 404 });
  }
}
