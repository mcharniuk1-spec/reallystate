"use client";

import { useState, useCallback } from "react";
import { proxyImageUrl } from "@/lib/utils/image-url";

type Props = {
  images: string[];
  alt: string;
  aspectRatio?: string;
  sourceName?: string;
};

export function PhotoCarousel({
  images,
  alt,
  aspectRatio = "aspect-[16/10]",
  sourceName,
}: Props) {
  const [idx, setIdx] = useState(0);
  const [failedSet, setFailed] = useState<Set<number>>(new Set());

  const prev = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIdx((i) => (i > 0 ? i - 1 : images.length - 1));
    },
    [images.length],
  );

  const next = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIdx((i) => (i < images.length - 1 ? i + 1 : 0));
    },
    [images.length],
  );

  if (images.length === 0) {
    return (
      <div
        className={`${aspectRatio} rounded-xl bg-gradient-to-br from-paper to-line/40 border border-line/50 flex items-center justify-center overflow-hidden`}
      >
        <div className="text-center px-4">
          <svg
            className="mx-auto text-mist/30"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <rect x="3" y="3" width="18" height="18" rx="3" />
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
            <path d="M21 15l-5-5L5 21" />
          </svg>
          <p className="mt-2 text-[10px] font-medium text-mist/50 uppercase tracking-wider">
            {sourceName || "No photos"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`group/carousel relative ${aspectRatio} rounded-xl overflow-hidden bg-paper border border-line/50`}>
      {/* Current image */}
      <img
        src={proxyImageUrl(images[idx])}
        alt={`${alt} — photo ${idx + 1}`}
        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-200 ${failedSet.has(idx) ? "hidden" : ""}`}
        loading="lazy"
        onError={() => setFailed((prev) => new Set(prev).add(idx))}
      />
      {failedSet.has(idx) && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-paper to-line/40">
          <div className="text-center px-4">
            <svg className="mx-auto text-mist/30" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="3" />
              <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
            <p className="mt-1 text-[9px] text-mist/50">Loading...</p>
          </div>
        </div>
      )}

      {/* Gradient overlays for buttons */}
      {images.length > 1 && (
        <>
          <div className="absolute inset-y-0 left-0 w-12 bg-gradient-to-r from-ink/20 to-transparent opacity-0 group-hover/carousel:opacity-100 transition-opacity pointer-events-none" />
          <div className="absolute inset-y-0 right-0 w-12 bg-gradient-to-l from-ink/20 to-transparent opacity-0 group-hover/carousel:opacity-100 transition-opacity pointer-events-none" />
        </>
      )}

      {/* Prev/Next arrows */}
      {images.length > 1 && (
        <>
          <button
            type="button"
            onClick={prev}
            className="absolute left-1.5 top-1/2 -translate-y-1/2 flex h-7 w-7 items-center justify-center rounded-full bg-white/80 text-ink shadow-sm opacity-0 group-hover/carousel:opacity-100 transition-opacity hover:bg-white"
            aria-label="Previous photo"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          <button
            type="button"
            onClick={next}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 flex h-7 w-7 items-center justify-center rounded-full bg-white/80 text-ink shadow-sm opacity-0 group-hover/carousel:opacity-100 transition-opacity hover:bg-white"
            aria-label="Next photo"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </>
      )}

      {/* Dot indicators */}
      {images.length > 1 && images.length <= 8 && (
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
          {images.map((_, i) => (
            <span
              key={i}
              className={`block h-1.5 rounded-full transition-all ${
                i === idx ? "w-4 bg-white" : "w-1.5 bg-white/50"
              }`}
            />
          ))}
        </div>
      )}

      {/* Photo count badge */}
      {images.length > 1 && (
        <span className="absolute top-2 right-2 flex items-center gap-1 rounded-full bg-ink/60 px-2 py-0.5 text-[10px] font-semibold text-white backdrop-blur-sm">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="3" />
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
            <path d="M21 15l-5-5L5 21" />
          </svg>
          {idx + 1}/{images.length}
        </span>
      )}
    </div>
  );
}

export function PhotoGallery({
  images,
  alt,
}: {
  images: string[];
  alt: string;
}) {
  const [current, setCurrent] = useState(0);
  const [lightbox, setLightbox] = useState(false);

  if (images.length === 0) {
    return (
      <div className="aspect-[16/10] rounded-3xl border border-line bg-gradient-to-br from-panel to-line/30 shadow-inner flex items-center justify-center">
        <div className="text-center px-8">
          <svg className="mx-auto text-mist/30" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="3" width="18" height="18" rx="3" />
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
            <path d="M21 15l-5-5L5 21" />
          </svg>
          <p className="mt-3 text-xs font-medium text-mist/50 uppercase tracking-wider">
            Photo pipeline not yet connected
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Main image */}
      <div className="space-y-2">
        <div
          className="relative aspect-[16/10] rounded-3xl overflow-hidden border border-line cursor-pointer group"
          onClick={() => setLightbox(true)}
        >
          <img
            src={proxyImageUrl(images[current])}
            alt={`${alt} — photo ${current + 1}`}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-ink/0 group-hover:bg-ink/10 transition-colors flex items-center justify-center">
            <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 rounded-full p-3 shadow-lg">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 3 21 3 21 9" />
                <polyline points="9 21 3 21 3 15" />
                <line x1="21" y1="3" x2="14" y2="10" />
                <line x1="3" y1="21" x2="10" y2="14" />
              </svg>
            </div>
          </div>
          {images.length > 1 && (
            <span className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full bg-ink/60 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="3" />
              </svg>
              {images.length} photos
            </span>
          )}
        </div>

        {/* Thumbnail strip */}
        {images.length > 1 && (
          <div className="flex gap-2 overflow-x-auto pb-1">
            {images.map((url, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setCurrent(i)}
                className={`shrink-0 h-16 w-24 rounded-xl overflow-hidden border-2 transition-all ${
                  i === current ? "border-sea ring-1 ring-sea/30" : "border-transparent opacity-60 hover:opacity-100"
                }`}
              >
                <img src={proxyImageUrl(url)} alt={`Thumbnail ${i + 1}`} className="w-full h-full object-cover" loading="lazy" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-[100] bg-ink/95 flex items-center justify-center"
          onClick={() => setLightbox(false)}
        >
          <button
            type="button"
            onClick={() => setLightbox(false)}
            className="absolute top-4 right-4 rounded-full bg-white/10 p-2 text-white hover:bg-white/20 transition-colors"
            aria-label="Close"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setCurrent((i) => (i > 0 ? i - 1 : images.length - 1));
            }}
            className="absolute left-4 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-3 text-white hover:bg-white/20 transition-colors"
            aria-label="Previous"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>

          <img
            src={proxyImageUrl(images[current])}
            alt={`${alt} — full photo ${current + 1}`}
            className="max-h-[85vh] max-w-[90vw] object-contain rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setCurrent((i) => (i < images.length - 1 ? i + 1 : 0));
            }}
            className="absolute right-4 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-3 text-white hover:bg-white/20 transition-colors"
            aria-label="Next"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>

          <span className="absolute bottom-6 left-1/2 -translate-x-1/2 text-white/80 text-sm font-medium">
            {current + 1} / {images.length}
          </span>
        </div>
      )}
    </>
  );
}
