from __future__ import annotations

import os

import uvicorn

from .api.main import create_app


def main() -> int:
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    app = create_app()
    print(f"API listening on http://{host}:{port}")
    print("Routes: /health, /sources, /status, /api/v1/chat (POST), /api/v1/ready")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
