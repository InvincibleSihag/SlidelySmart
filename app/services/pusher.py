"""Pusher client for real-time notification events.

Sends lightweight pings (status changes, completion, errors) so clients
know when to re-fetch via the GET job endpoint.  No heavy payloads.
"""

from pusher import Pusher

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

pusher_client: Pusher = Pusher(
    app_id=settings.pusher_app_id,
    key=settings.pusher_key,
    secret=settings.pusher_secret,
    cluster=settings.pusher_cluster,
    ssl=True,
)


def trigger(channel: str, event: str, data: dict) -> None:
    """Fire-and-forget: send *data* on *channel/event*.

    Errors are logged and swallowed — a notification failure never crashes the caller.
    """
    try:
        pusher_client.trigger(channel, event, data)
    except Exception:
        logger.exception("pusher_trigger_failed", channel=channel, pusher_event=event)
