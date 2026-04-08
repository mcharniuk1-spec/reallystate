import { NextRequest, NextResponse } from "next/server";

const GRADIENTS: [string, string][] = [
  ["#0b6b57", "#0d8a72"],
  ["#1a4a5e", "#2d7d9a"],
  ["#4a3b6e", "#7c5fad"],
  ["#6b4a3b", "#a07858"],
  ["#3b5e4a", "#5a9a6e"],
  ["#5e3b4a", "#9a5a7e"],
];

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ params: string[] }> },
) {
  const segments = (await params).params;
  const width = parseInt(segments[0] ?? "800", 10) || 800;
  const height = parseInt(segments[1] ?? "500", 10) || 500;

  const url = new URL(request.url);
  const text = url.searchParams.get("text") ?? "Property";
  const label = decodeURIComponent(text).replace(/\+/g, " ");

  const hash = label.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const [c1, c2] = GRADIENTS[hash % GRADIENTS.length];

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${c1}" />
      <stop offset="100%" stop-color="${c2}" />
    </linearGradient>
  </defs>
  <rect width="${width}" height="${height}" fill="url(#g)" />
  <text x="50%" y="45%" text-anchor="middle" dominant-baseline="middle" fill="white" font-family="system-ui,sans-serif" font-size="${Math.max(16, Math.min(28, width / 20))}" font-weight="600" opacity="0.9">${escapeXml(label)}</text>
  <text x="50%" y="58%" text-anchor="middle" dominant-baseline="middle" fill="white" font-family="system-ui,sans-serif" font-size="12" opacity="0.5">${width}×${height} · placeholder</text>
</svg>`;

  return new NextResponse(svg, {
    headers: {
      "Content-Type": "image/svg+xml",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}

function escapeXml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
