from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from ...source_registry import SourceRegistry

router = APIRouter(tags=["system"])

ROOT = Path(__file__).resolve().parents[4]
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


@router.get("/health")
@router.get("/")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "bgrealestate-api",
        "runtime": "fastapi",
        "stage": os.getenv("DEPLOY_STAGE", "local_dev"),
    }


@router.get("/sources")
def sources() -> dict[str, Any]:
    return _registry_payload()


@router.get("/status")
def status() -> dict[str, Any]:
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8") if ROADMAP_PATH.exists() else ""
    done = roadmap.count("- [x]")
    total = roadmap.count("- [")
    return {
        "roadmap": str(ROADMAP_PATH),
        "done": done,
        "total": total,
        "remaining": total - done,
    }
