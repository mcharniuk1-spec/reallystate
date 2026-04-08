from __future__ import annotations

import os
import sys

import uvicorn


def main() -> int:
    if sys.version_info < (3, 12):
        print(
            (
                "bgrealestate requires Python 3.12+ for API runtime. "
                f"Detected {sys.version.split(' ')[0]}. "
                "Use `make run-api` (auto-selects newer Python when available) "
                "or run with python3.12 explicitly."
            ),
            file=sys.stderr,
        )
        return 1

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    from .api.main import create_app

    app = create_app()
    print(f"API listening on http://{host}:{port}")
    print("Routes: /health, /sources, /status, /api/v1/chat (POST), /api/v1/ready")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
