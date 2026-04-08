import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
const CACHE_SECONDS = 86400 * 7;

/**
 * Image proxy route for the frontend.
 *
 * Usage:
 *   /api/images?url=<encoded-external-url>
 *   /api/images?media_id=<listing-media-id>
 *
 * Proxies through the FastAPI backend when available, or directly
 * fetches the external URL when the backend is unreachable.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const externalUrl = searchParams.get("url");
  const mediaId = searchParams.get("media_id");

  if (!externalUrl && !mediaId) {
    return NextResponse.json(
      { error: "Provide ?url=<image-url> or ?media_id=<id>" },
      { status: 400 },
    );
  }

  try {
    if (mediaId) {
      const backendResp = await fetch(`${BACKEND_URL}/media/${mediaId}`, {
        signal: AbortSignal.timeout(10_000),
      });
      if (backendResp.ok) {
        const ct = backendResp.headers.get("content-type") ?? "image/jpeg";
        const buf = await backendResp.arrayBuffer();
        return new NextResponse(buf, {
          headers: {
            "Content-Type": ct,
            "Cache-Control": `public, max-age=${CACHE_SECONDS}`,
          },
        });
      }
    }

    if (externalUrl) {
      const decoded = decodeURIComponent(externalUrl);
      if (!/^https?:\/\//.test(decoded)) {
        return NextResponse.json({ error: "Invalid URL" }, { status: 400 });
      }

      // Try backend proxy first (handles auth headers, rate limiting)
      try {
        const backendProxy = await fetch(
          `${BACKEND_URL}/media/proxy?url=${encodeURIComponent(decoded)}`,
          { signal: AbortSignal.timeout(10_000) },
        );
        if (backendProxy.ok) {
          const ct = backendProxy.headers.get("content-type") ?? "image/jpeg";
          const buf = await backendProxy.arrayBuffer();
          return new NextResponse(buf, {
            headers: {
              "Content-Type": ct,
              "Cache-Control": `public, max-age=${CACHE_SECONDS}`,
            },
          });
        }
      } catch {
        // Backend unavailable, fall through to direct fetch
      }

      // Direct fetch as fallback
      const directResp = await fetch(decoded, {
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; BulgariaRealEstate/0.1)",
          Accept: "image/*",
        },
        signal: AbortSignal.timeout(15_000),
      });

      if (!directResp.ok) {
        return NextResponse.json(
          { error: `Upstream returned ${directResp.status}` },
          { status: 502 },
        );
      }

      const ct = directResp.headers.get("content-type") ?? "image/jpeg";
      const buf = await directResp.arrayBuffer();
      return new NextResponse(buf, {
        headers: {
          "Content-Type": ct,
          "Cache-Control": `public, max-age=${CACHE_SECONDS}`,
        },
      });
    }

    return NextResponse.json({ error: "Image not found" }, { status: 404 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
