from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from ..source_registry import SourceRegistry


@dataclass(frozen=True)
class TemporalSettings:
    address: str
    namespace: str
    task_queue: str


def load_temporal_settings() -> TemporalSettings:
    return TemporalSettings(
        address=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
        task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "bgrealestate-main"),
    )


def temporal_enabled() -> bool:
    return os.getenv("ENABLE_TEMPORAL_RUNTIME", "").strip().lower() in {"1", "true", "yes", "on"}


def _import_temporal() -> tuple[Any, Any, Any, Any]:
    from temporalio import activity, workflow
    from temporalio.client import Client
    from temporalio.worker import Worker

    return activity, workflow, Client, Worker


def _registry_path(path: str | None) -> Path:
    if path:
        return Path(path)
    return Path(__file__).resolve().parents[3] / "data" / "source_registry.json"


async def temporal_connectivity_check() -> dict[str, str]:
    _, _, Client, _ = _import_temporal()
    s = load_temporal_settings()
    client = await Client.connect(s.address, namespace=s.namespace)
    return {"address": s.address, "namespace": s.namespace, "task_queue": s.task_queue, "status": "connected"}


async def run_temporal_scheduler_once(*, registry_path: str | None = None) -> dict[str, str]:
    activity, workflow, Client, _ = _import_temporal()
    s = load_temporal_settings()
    client = await Client.connect(s.address, namespace=s.namespace)

    @activity.defn(name="discover_sources_activity")
    def discover_sources_activity(path: str) -> list[str]:
        reg = SourceRegistry.from_file(Path(path))
        return [e.source_name for e in reg.all()]

    @workflow.defn(name="SourceDiscoveryWorkflow")
    class SourceDiscoveryWorkflow:
        @workflow.run
        async def run(self, registry_json_path: str) -> dict[str, Any]:
            sources = await workflow.execute_activity(
                discover_sources_activity,
                registry_json_path,
                start_to_close_timeout=timedelta(seconds=30),
            )
            return {"source_count": len(sources)}

    workflow_id = f"source-discovery-once-{int(asyncio.get_running_loop().time())}"
    handle = await client.start_workflow(
        "SourceDiscoveryWorkflow",
        str(_registry_path(registry_path)),
        id=workflow_id,
        task_queue=s.task_queue,
    )
    return {"started": workflow_id, "run_id": handle.first_execution_run_id}


async def run_temporal_worker_forever() -> None:
    activity, workflow, Client, Worker = _import_temporal()
    s = load_temporal_settings()
    client = await Client.connect(s.address, namespace=s.namespace)

    @activity.defn(name="discover_sources_activity")
    def discover_sources_activity(path: str) -> list[str]:
        reg = SourceRegistry.from_file(Path(path))
        return [e.source_name for e in reg.all()]

    @activity.defn(name="listing_detail_activity")
    def listing_detail_activity(source_name: str, listing_url: str) -> dict[str, str]:
        return {"source_name": source_name, "listing_url": listing_url, "status": "queued"}

    @workflow.defn(name="SourceDiscoveryWorkflow")
    class SourceDiscoveryWorkflow:
        @workflow.run
        async def run(self, registry_json_path: str) -> dict[str, Any]:
            sources = await workflow.execute_activity(
                discover_sources_activity,
                registry_json_path,
                start_to_close_timeout=timedelta(seconds=30),
            )
            return {"source_count": len(sources)}

    @workflow.defn(name="ListingDetailWorkflow")
    class ListingDetailWorkflow:
        @workflow.run
        async def run(self, source_name: str, listing_url: str) -> dict[str, str]:
            return await workflow.execute_activity(
                listing_detail_activity,
                source_name,
                listing_url,
                start_to_close_timeout=timedelta(seconds=30),
            )

    worker = Worker(
        client,
        task_queue=s.task_queue,
        workflows=[SourceDiscoveryWorkflow, ListingDetailWorkflow],
        activities=[discover_sources_activity, listing_detail_activity],
    )
    await worker.run()

