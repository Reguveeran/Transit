import os
import sys
import subprocess
import time
from typing import List, Dict, Any, Optional

from workers.common.redis_client import get_redis_client, STREAM_KEY, CONSUMER_GROUP


def get_workspace_dir() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )


def get_venv_python() -> str:
    workspace_dir = get_workspace_dir()
    venv_python = os.path.join(workspace_dir, ".venv", "bin", "python")
    return venv_python if os.path.exists(venv_python) else sys.executable


def list_active_workers() -> List[Dict[str, Any]]:
    """
    Inspects Redis consumer group 'unitransit_workers' on 'transport.events'.
    Purges stale abandoned consumers and returns live active worker statuses.
    """
    workers = []
    try:
        r = get_redis_client()
        consumers = r.xinfo_consumers(STREAM_KEY, CONSUMER_GROUP)

        # 1. Inspect consumers & purge long-abandoned (> 60s idle with 0 pending)
        for c in consumers:
            c_name = str(c.get("name", ""))
            idle_ms = c.get("idle", 0)
            pending_count = c.get("pending", 0)

            if idle_ms > 60000 and pending_count == 0:
                try:
                    r.xgroup_delconsumer(STREAM_KEY, CONSUMER_GROUP, c_name)
                    continue
                except Exception:
                    pass

            idle_sec = round(idle_ms / 1000.0, 2)
            is_active = idle_ms < 30000

            workers.append({
                "name": c_name,
                "status": "HEALTHY" if is_active else "DOWN",
                "pending_messages": pending_count,
                "idle_seconds": idle_sec,
                "active": is_active,
            })

    except Exception as e:
        # Fallback if Redis offline
        workers = [
            {"name": "position-worker-1", "status": "UNAVAILABLE", "pending_messages": 0, "idle_seconds": 99.0, "active": False}
        ]

    return workers


def scale_workers_pool(target: int) -> Dict[str, Any]:
    """
    Scales the worker pool horizontally between 1, 2, 3, or more workers.
    """
    target = max(1, min(5, target))
    workspace_dir = get_workspace_dir()
    venv_python = get_venv_python()

    current_workers = list_active_workers()
    active_count = sum(1 for w in current_workers if w.get("active"))

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.path.join(workspace_dir, 'backend')}:{workspace_dir}"

    logs = [f"[T+0.0s] WorkerScaleManager requested scale: {active_count} → {target}"]

    if active_count < target:
        needed = target - active_count
        for i in range(needed):
            worker_id = f"position-worker-{active_count + i + 1}"
            cmd = [venv_python, "workers/position_worker/position_worker.py", "--consumer-name", worker_id]
            subprocess.Popen(cmd, cwd=workspace_dir, env=env)
            logs.append(f"[T+0.{i+2}s] Spawned new worker process '{worker_id}'")

    elif active_count > target:
        surplus = active_count - target
        active_names = [w["name"] for w in current_workers if w.get("active")]
        to_kill = active_names[-surplus:]
        for name in to_kill:
            subprocess.run(["pkill", "-f", f"--consumer-name {name}"], capture_output=True)
            logs.append(f"[T+0.4s] Sent SIGTERM to surplus worker '{name}'")

    time.sleep(0.5)
    updated_workers = list_active_workers()

    return {
        "status": "scaled",
        "target": target,
        "active": sum(1 for w in updated_workers if w.get("active")),
        "workers": updated_workers,
        "logs": logs,
    }


def kill_specific_worker(worker_id: str) -> Dict[str, Any]:
    """
    Kills a designated worker (e.g. position-worker-2) to demonstrate
    unacknowledged PEL buildup and subsequent recovery by surviving workers.
    """
    logs = [f"[T+0.0s] WorkerScaleManager sending SIGTERM to '{worker_id}'"]
    try:
        res = subprocess.run(["pkill", "-f", f"--consumer-name {worker_id}"], capture_output=True)
        logs.append(f"[T+0.4s] Process '{worker_id}' terminated.")
        logs.append("[T+0.8s] Unacknowledged messages remain in Redis PEL under this consumer.")
        logs.append("[T+1.2s] Surviving workers will reclaim messages via xautoclaim after min_idle threshold.")
        status_val = "killed"
    except Exception as e:
        logs.append(f"[ERROR] {e}")
        status_val = "failed"

    time.sleep(0.3)
    updated = list_active_workers()
    return {
        "status": status_val,
        "killed_worker": worker_id,
        "surviving_workers": updated,
        "logs": logs,
    }


def ensure_worker_count(count: int = 2) -> Dict[str, Any]:
    """Ensures at least `count` workers are running."""
    current = list_active_workers()
    active_count = sum(1 for w in current if w.get("active"))
    if active_count < count:
        return scale_workers_pool(count)
    return {"active": active_count, "workers": current}
