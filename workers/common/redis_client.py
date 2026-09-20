"""
UniTransit - Common Redis Streaming & Pub/Sub Client
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("unitransit.redis")

STREAM_KEY = os.getenv("REDIS_STREAM_KEY", "transport.events")
CONSUMER_GROUP = os.getenv("REDIS_GROUP_NAME", "unitransit_workers")
CHANNEL_VEHICLE_UPDATES = "vehicle.updates"
CHANNEL_ALERTS = "alerts"


def get_redis_client():
    import redis

    try:
        from django.conf import settings
        redis_host = getattr(settings, "REDIS_HOST", os.getenv("REDIS_HOST", "localhost"))
        redis_port = int(getattr(settings, "REDIS_PORT", os.getenv("REDIS_PORT", 6379)))
        redis_db = int(getattr(settings, "REDIS_DB", os.getenv("REDIS_DB", 0)))
    except Exception:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))

    return redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True,
        socket_connect_timeout=2.0,
    )


def ensure_consumer_group(redis_client, stream_key: str = STREAM_KEY, group_name: str = CONSUMER_GROUP):
    """Ensures that the Redis stream and consumer group exist."""
    try:
        redis_client.xgroup_create(stream_key, group_name, id="0", mkstream=True)
        logger.info(f"Created consumer group '{group_name}' on stream '{stream_key}'.")
    except Exception as e:
        if "BUSYGROUP" in str(e):
            # Group already exists, which is normal
            pass
        else:
            logger.warning(f"Consumer group init note: {e}")


def publish_to_channel(redis_client, channel: str, message: Dict[str, Any]):
    """Publishes JSON message to a Redis Pub/Sub channel."""
    try:
        redis_client.publish(channel, json.dumps(message))
    except Exception as e:
        logger.error(f"Error publishing to {channel}: {e}")
