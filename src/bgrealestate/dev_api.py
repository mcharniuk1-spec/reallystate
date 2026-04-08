from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .source_registry import SourceRegistry


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "data" / "source_registry.json"
ROADMAP_PATH = ROOT / "docs" / "project-status-roadmap.md"


def _registry_payload() -> dict[str, Any]:
    registry = SourceRegistry.from_file(REGISTRY_PATH)
    sources = [
        {
            "source_name": entry.source_name,
            "tier": entry.tier,
            "family": entry.source_family.value,
            "access_mode": entry.access_mode.value,
            "legal_mode": entry.legal_mode,
            "risk_mode": entry.risk_mode.value,
            "mvp_phase": entry.mvp_phase,
            "primary_url": entry.primary_url,
        }
        for entry in registry.all()
    ]
    return {"count": len(sources), "sources": sources}


class DevStatusHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/health"}:
            self._send_json(
                {
                    "status": "ok",
                    "service": "bgrealestate-dev-api",
                    "stage": "development_environment_setup",
                    "note": "Lightweight stdlib dev API. Replace with FastAPI in the backend API phase.",
                }
            )
            return
        if path == "/sources":
            self._send_json(_registry_payload())
            return
        if path == "/status":
            roadmap = ROADMAP_PATH.read_text(encoding="utf-8") if ROADMAP_PATH.exists() else ""
            done = roadmap.count("- [x]")
            total = roadmap.count("- [")
            self._send_json({"roadmap": str(ROADMAP_PATH), "done": done, "total": total, "remaining": total - done})
            return
        self._send_json({"error": "not_found", "available": ["/health", "/sources", "/status"]}, status=404)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"dev-api: {format % args}")


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), DevStatusHandler)
    print("dev API listening on http://127.0.0.1:8000")
    print("available endpoints: /health, /sources, /status")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
