from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import admin, analytics, chat, crawl_jobs, crm, listings, media, properties, readiness, system, user_auth, users


def create_app() -> FastAPI:
    app = FastAPI(
        title="Bulgaria Real Estate API",
        version="0.1.0",
        description="Ingestion, CRM, map, and assistant backends for the MVP.",
    )
    origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(system.router)
    app.include_router(listings.router)
    app.include_router(crm.router)
    app.include_router(crawl_jobs.router)
    app.include_router(properties.router)
    app.include_router(analytics.router)
    app.include_router(admin.router)
    app.include_router(user_auth.router)
    app.include_router(users.router)
    app.include_router(media.router)
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(readiness.router, prefix="/api/v1")
    return app
