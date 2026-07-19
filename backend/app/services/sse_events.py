"""SSE (Server-Sent Events) — live queue status updates.

Provides real-time updates when posts are published, fail, or
the queue state changes.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)

# In-memory event queue (production: use Redis pub/sub)
_event_queues: dict[str, list[asyncio.Queue]] = {}


async def publish_event(event_type: str, data: dict[str, Any], workspace_id: str = "all"):
    """Publish an event to all subscribers of a workspace."""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    event_json = json.dumps(event)

    # Send to workspace-specific subscribers
    queues = _event_queues.get(workspace_id, []) + _event_queues.get("all", [])
    for queue in queues:
        try:
            queue.put_nowait(event_json)
        except asyncio.QueueFull:
            logger.warning("SSE event queue full, dropping event")


async def subscribe_events(workspace_id: str) -> AsyncGenerator[str, None]:
    """Subscribe to events for a workspace. Yields SSE-formatted strings."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    if workspace_id not in _event_queues:
        _event_queues[workspace_id] = []
    _event_queues[workspace_id].append(queue)

    try:
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'workspace': workspace_id})}\n\n"

        while True:
            try:
                event_json = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"data: {event_json}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive
                yield f": keepalive {datetime.utcnow().isoformat()}\n\n"
    finally:
        if workspace_id in _event_queues:
            _event_queues[workspace_id].remove(queue)


async def notify_publish_started(post_id: str, platform: str, workspace_id: str):
    """Notify subscribers that a publish has started."""
    await publish_event("publish_started", {
        "post_id": post_id,
        "platform": platform,
    }, workspace_id)


async def notify_publish_completed(post_id: str, platform: str, platform_post_id: str, workspace_id: str):
    """Notify subscribers that a publish completed."""
    await publish_event("publish_completed", {
        "post_id": post_id,
        "platform": platform,
        "platform_post_id": platform_post_id,
    }, workspace_id)


async def notify_publish_failed(post_id: str, platform: str, error: str, workspace_id: str):
    """Notify subscribers that a publish failed."""
    await publish_event("publish_failed", {
        "post_id": post_id,
        "platform": platform,
        "error": error,
    }, workspace_id)


async def notify_queue_updated(workspace_id: str):
    """Notify subscribers that the queue has been updated."""
    await publish_event("queue_updated", {}, workspace_id)
