import { NextResponse } from "next/server";

import { getApiBaseUrl } from "@/lib/config";

type Ctx = { params: Promise<{ path?: string[] }> };

const TIMEOUT_MS = 60_000;

async function proxy(req: Request, ctx: Ctx) {
  const { path: segments } = await ctx.params;
  const tail = (segments ?? []).join("/");
  const base = getApiBaseUrl();
  const url = tail ? `${base}/${tail}` : `${base}/health`;
  const method = req.method.toUpperCase();
  const headers = new Headers();
  const ct = req.headers.get("content-type");
  if (ct) headers.set("content-type", ct);
  const init: RequestInit = {
    method,
    headers,
    cache: "no-store",
    signal: AbortSignal.timeout(TIMEOUT_MS),
  };
  if (method !== "GET" && method !== "HEAD") {
    const buf = await req.arrayBuffer();
    if (buf.byteLength > 0) {
      init.body = buf;
    }
  }
  try {
    const res = await fetch(url, init);
    const outCt = res.headers.get("Content-Type") ?? "application/json; charset=utf-8";
    const body = await res.text();
    return new NextResponse(body, { status: res.status, headers: { "Content-Type": outCt } });
  } catch {
    return NextResponse.json(
      { error: "upstream_unreachable", detail: `No response from ${base}` },
      { status: 503 },
    );
  }
}

export async function GET(req: Request, ctx: Ctx) {
  return proxy(req, ctx);
}

export async function POST(req: Request, ctx: Ctx) {
  return proxy(req, ctx);
}

export async function PUT(req: Request, ctx: Ctx) {
  return proxy(req, ctx);
}

export async function PATCH(req: Request, ctx: Ctx) {
  return proxy(req, ctx);
}

export async function DELETE(req: Request, ctx: Ctx) {
  return proxy(req, ctx);
}
