/**
 * Transform an image URL for reliable frontend display.
 *
 * - Internal paths (starting with /) are left as-is
 * - External URLs are routed through /api/images?url=<encoded>
 * - Media IDs use /api/images?media_id=<id>
 */
export function proxyImageUrl(url: string): string {
  if (!url) return "";
  if (url.startsWith("/")) return url;
  if (url.startsWith("data:")) return url;
  return `/api/images?url=${encodeURIComponent(url)}`;
}

export function mediaIdUrl(mediaId: string): string {
  return `/api/images?media_id=${encodeURIComponent(mediaId)}`;
}

/**
 * Transform a list of image URLs, routing external ones through the proxy.
 */
export function proxyImageUrls(urls: string[]): string[] {
  return urls.map(proxyImageUrl);
}
