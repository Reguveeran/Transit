import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from apps.devops.models import Incident


def evaluate_system_incidents(metrics: Dict[str, Any]) -> None:
    """
    Evaluates real-time system metrics against SRE thresholds and
    automatically opens or resolves incidents with exact telemetry.
    """
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%H:%M:%S")

    # -------------------------------------------------------------
    # 1. Rule: Redis Consumer Lag Alert
    # -------------------------------------------------------------
    consumer_lag = float(metrics.get("consumer_lag_sec", 0.0))
    pending_messages = int(metrics.get("pending_messages", 0))
    lag_threshold = 5.0
    pel_threshold = 20

    lag_inc = Incident.objects.filter(incident_id="INC-LAG-001").first()
    is_lag_breached = (consumer_lag >= lag_threshold) or (pending_messages >= pel_threshold)

    if is_lag_breached:
        if not lag_inc or lag_inc.status == "RESOLVED":
            # Open new incident
            Incident.objects.update_or_create(
                incident_id="INC-LAG-001",
                defaults={
                    "title": "Redis Consumer Lag Exceeded Threshold",
                    "severity": "HIGH",
                    "status": "INVESTIGATING",
                    "affected_service": "PositionWorker (Consumer Group: unitransit_workers)",
                    "timeline": [
                        {
                            "time": time_str,
                            "event": f"Consumer lag reached {consumer_lag:.2f}s (Threshold: {lag_threshold}s, PEL: {pending_messages} messages)",
                        }
                    ],
                    "metadata": {
                        "threshold": lag_threshold,
                        "current": consumer_lag,
                        "peak": consumer_lag,
                        "pel": pending_messages,
                        "metric": "consumer_lag_sec",
                    },
                    "created_at": now,
                    "resolved_at": None,
                },
            )
        else:
            # Update active incident peak
            meta = lag_inc.metadata or {}
            current_peak = meta.get("peak", 0.0)
            if consumer_lag > current_peak:
                meta["peak"] = round(consumer_lag, 2)
            meta["current"] = round(consumer_lag, 2)
            meta["pel"] = pending_messages
            lag_inc.metadata = meta
            lag_inc.save(update_fields=["metadata", "updated_at"])

    elif lag_inc and lag_inc.status != "RESOLVED":
        # Check auto-recovery
        if consumer_lag < 2.0 and pending_messages < 5:
            duration = round((now - lag_inc.created_at).total_seconds(), 1)
            meta = lag_inc.metadata or {}
            meta["duration"] = duration
            meta["current"] = consumer_lag
            meta["recovery"] = "Automatic"
            timeline = lag_inc.timeline or []
            timeline.append({
                "time": time_str,
                "event": f"Consumer lag drained to {consumer_lag:.2f}s. System recovered automatically.",
            })
            lag_inc.status = "RESOLVED"
            lag_inc.resolved_at = now
            lag_inc.timeline = timeline
            lag_inc.metadata = meta
            lag_inc.postmortem = (
                f"Peak lag was {meta.get('peak', consumer_lag)}s under load. "
                f"PositionWorker consumer group successfully recovered PEL within {duration}s."
            )
            lag_inc.save()

    # -------------------------------------------------------------
    # 2. Rule: Redis Outage Alert
    # -------------------------------------------------------------
    redis_healthy = bool(metrics.get("redis_healthy", True))
    redis_inc = Incident.objects.filter(incident_id="INC-REDIS-001").first()

    if not redis_healthy:
        if not redis_inc or redis_inc.status == "RESOLVED":
            Incident.objects.update_or_create(
                incident_id="INC-REDIS-001",
                defaults={
                    "title": "Redis Stream Broker Unreachable",
                    "severity": "CRITICAL",
                    "status": "INVESTIGATING",
                    "affected_service": "Redis Stream Broker (port 6380)",
                    "timeline": [
                        {
                            "time": time_str,
                            "event": "Redis PING failed. Connection refused or broker paused.",
                        }
                    ],
                    "metadata": {"type": "connectivity", "target": "redis"},
                    "created_at": now,
                    "resolved_at": None,
                },
            )
    elif redis_inc and redis_inc.status != "RESOLVED":
        duration = round((now - redis_inc.created_at).total_seconds(), 1)
        meta = redis_inc.metadata or {}
        meta["duration"] = duration
        meta["recovery"] = "Automatic"
        timeline = redis_inc.timeline or []
        timeline.append({
            "time": time_str,
            "event": "Redis broker connectivity restored. PONG received.",
        })
        redis_inc.status = "RESOLVED"
        redis_inc.resolved_at = now
        redis_inc.timeline = timeline
        redis_inc.metadata = meta
        redis_inc.postmortem = f"Redis broker was offline for {duration}s. Background worker reconnected."
        redis_inc.save()

    # -------------------------------------------------------------
    # 3. Rule: PostgreSQL Outage Alert
    # -------------------------------------------------------------
    db_healthy = bool(metrics.get("db_healthy", True))
    db_inc = Incident.objects.filter(incident_id="INC-DB-001").first()

    if not db_healthy:
        if not db_inc or db_inc.status == "RESOLVED":
            Incident.objects.update_or_create(
                incident_id="INC-DB-001",
                defaults={
                    "title": "PostgreSQL Primary Connection Dropped",
                    "severity": "CRITICAL",
                    "status": "INVESTIGATING",
                    "affected_service": "PostgreSQL / PostGIS Database",
                    "timeline": [
                        {
                            "time": time_str,
                            "event": "Database probe SELECT 1 failed.",
                        }
                    ],
                    "metadata": {"type": "connectivity", "target": "postgres"},
                    "created_at": now,
                    "resolved_at": None,
                },
            )
    elif db_inc and db_inc.status != "RESOLVED":
        duration = round((now - db_inc.created_at).total_seconds(), 1)
        meta = db_inc.metadata or {}
        meta["duration"] = duration
        meta["recovery"] = "Automatic"
        timeline = db_inc.timeline or []
        timeline.append({
            "time": time_str,
            "event": "Database connection restored. SELECT 1 query succeeded.",
        })
        db_inc.status = "RESOLVED"
        db_inc.resolved_at = now
        db_inc.timeline = timeline
        db_inc.metadata = meta
        db_inc.save()

    # -------------------------------------------------------------
    # 4. Rule: Worker Process Down
    # -------------------------------------------------------------
    active_workers = int(metrics.get("active_workers", 0))
    worker_inc = Incident.objects.filter(incident_id="INC-WORKER-001").first()

    # If Redis is healthy but 0 workers active for > 30s
    if redis_healthy and active_workers == 0:
        if not worker_inc or worker_inc.status == "RESOLVED":
            Incident.objects.update_or_create(
                incident_id="INC-WORKER-001",
                defaults={
                    "title": "No Active Position Workers in Consumer Group",
                    "severity": "HIGH",
                    "status": "INVESTIGATING",
                    "affected_service": "PositionWorker Daemon",
                    "timeline": [
                        {
                            "time": time_str,
                            "event": "Zero active consumers detected in consumer group 'unitransit_workers'.",
                        }
                    ],
                    "metadata": {"type": "process_down", "target": "position_worker"},
                    "created_at": now,
                    "resolved_at": None,
                },
            )
    elif worker_inc and worker_inc.status != "RESOLVED" and active_workers > 0:
        duration = round((now - worker_inc.created_at).total_seconds(), 1)
        meta = worker_inc.metadata or {}
        meta["duration"] = duration
        meta["recovery"] = "Automatic"
        timeline = worker_inc.timeline or []
        timeline.append({
            "time": time_str,
            "event": f"Worker recovered. {active_workers} active consumer(s) joined group.",
        })
        worker_inc.status = "RESOLVED"
        worker_inc.resolved_at = now
        worker_inc.timeline = timeline
        worker_inc.metadata = meta
        worker_inc.save()
