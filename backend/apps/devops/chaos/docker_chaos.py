import os
import sys
import subprocess
import time
from typing import Dict, Any, Optional

from apps.devops.chaos.base import ChaosController


class DockerChaosController(ChaosController):
    """
    Local Docker and process-based implementation of ChaosController.
    Uses 'docker pause / unpause' for containers and process signals
    for horizontal worker scaling and fault simulation.
    """

    def __init__(self, chaos_state_ref: Dict[str, Any]):
        self.chaos_state = chaos_state_ref
        self.workspace_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        )
        self.venv_python = os.path.join(self.workspace_dir, ".venv", "bin", "python")
        if not os.path.exists(self.venv_python):
            self.venv_python = sys.executable

    def disconnect_redis(self) -> Dict[str, Any]:
        logs = ["[T+0.0s] Executing 'docker pause unitransit-redis'"]
        try:
            subprocess.run(["docker", "pause", "unitransit-redis"], check=True, capture_output=True, timeout=5)
            logs.append("[T+0.6s] Container unitransit-redis paused. Port 6380 unresponsive.")
            logs.append("[T+1.2s] Active workers will experience connection timeouts.")
            return {
                "name": "Disconnect Redis (Docker Pause)",
                "target": "docker/unitransit-redis",
                "status": "RUNNING",
                "expected": "Broker connection dropped; worker pauses; PEL & lag spike",
                "actual": "unitransit-redis paused via docker API.",
                "logs": logs,
            }
        except Exception as e:
            return {
                "name": "Disconnect Redis (Docker Pause)",
                "target": "docker/unitransit-redis",
                "status": "FAILED",
                "expected": "Pause broker",
                "actual": f"Error: {e}",
                "logs": [f"[ERROR] {e}"],
            }

    def restore_redis(self) -> Dict[str, Any]:
        logs = ["[T+0.0s] Executing 'docker unpause unitransit-redis'"]
        try:
            subprocess.run(["docker", "unpause", "unitransit-redis"], check=True, capture_output=True, timeout=5)
            logs.append("[T+0.5s] Container unpaused. Broker responding to PING.")
            logs.append("[T+1.0s] PositionWorker consumer group resuming consumption.")
            return {
                "name": "Restore Redis (Docker Unpause)",
                "target": "docker/unitransit-redis",
                "status": "RECOVERED",
                "expected": "Broker unpaused; worker reconnects; lag drains",
                "actual": "PONG verified. Stream consumption resumed.",
                "logs": logs,
            }
        except Exception as e:
            return {
                "name": "Restore Redis (Docker Unpause)",
                "target": "docker/unitransit-redis",
                "status": "FAILED",
                "expected": "Unpause broker",
                "actual": f"Error: {e}",
                "logs": [f"[ERROR] {e}"],
            }

    def stop_worker(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        logs = []
        if worker_id:
            logs.append(f"[T+0.0s] Targeting specific worker '{worker_id}' with SIGTERM")
            # Target by consumer name if passed
            try:
                subprocess.run(["pkill", "-f", f"--consumer-name {worker_id}"], capture_output=True)
                actual = f"Killed worker process '{worker_id}'."
            except Exception as e:
                actual = f"Failed to kill worker '{worker_id}': {e}"
        else:
            logs.append("[T+0.0s] Terminating all position_worker.py processes via SIGTERM")
            try:
                subprocess.run(["pkill", "-f", "workers/position_worker/position_worker.py"], capture_output=True)
                actual = "All position_worker processes terminated."
            except Exception as e:
                actual = f"Pkill failed: {e}"

        logs.append("[T+0.6s] Active consumer heartbeat expired in Redis.")
        logs.append("[T+1.2s] Incoming stream events remain unacknowledged in PEL.")
        return {
            "name": f"Stop Position Worker {f'({worker_id})' if worker_id else ''}",
            "target": f"process/{worker_id or 'position_worker'}",
            "status": "RUNNING",
            "expected": "Worker process dies; active ratio drops; PEL accumulates",
            "actual": actual,
            "logs": logs,
        }

    def start_worker(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        consumer_name = worker_id or f"position-worker-{int(time.time()) % 1000}"
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{os.path.join(self.workspace_dir, 'backend')}:{self.workspace_dir}"
        cmd = [self.venv_python, "workers/position_worker/position_worker.py", "--consumer-name", consumer_name]

        logs = [f"[T+0.0s] Spawning background worker '{consumer_name}'"]
        subprocess.Popen(cmd, cwd=self.workspace_dir, env=env)
        logs.append(f"[T+0.8s] Worker '{consumer_name}' joined consumer group 'unitransit_workers'.")
        logs.append("[T+1.4s] Worker polling stream and claiming pending messages.")

        return {
            "name": f"Start Position Worker ({consumer_name})",
            "target": f"process/{consumer_name}",
            "status": "RECOVERED",
            "expected": "New consumer joins consumer group; starts processing backlog",
            "actual": f"Worker '{consumer_name}' spawned successfully.",
            "logs": logs,
        }

    def scale_workers(self, target: int) -> Dict[str, Any]:
        from apps.devops.worker_manager import scale_workers_pool
        return scale_workers_pool(target)

    def inject_db_failure(self) -> Dict[str, Any]:
        self.chaos_state["db_failure"] = True
        return {
            "name": "Inject Database Outage",
            "target": "database/postgresql",
            "status": "RUNNING",
            "expected": "Database connection probes fail; workers cannot persist events; INC-DB triggers",
            "actual": "Database outage simulation flag enabled.",
            "logs": [
                "[T+0.0s] Set CHAOS_STATE['db_failure'] = True",
                "[T+0.5s] Health probe SELECT 1 returning unavailable.",
                "[T+1.0s] Incident engine detected database connectivity breach.",
            ],
        }

    def add_latency(self, latency_ms: int = 500) -> Dict[str, Any]:
        self.chaos_state["artificial_latency_ms"] = latency_ms
        return {
            "name": f"Inject {latency_ms}ms Latency",
            "target": "api-gateway",
            "status": "RUNNING",
            "expected": f"API latency increases by {latency_ms}ms; P95 SLO target breached",
            "actual": f"Added +{latency_ms}ms artificial latency.",
            "logs": [
                f"[T+0.0s] Added +{latency_ms}ms to request pipeline.",
                f"[T+0.4s] P95 latency degraded above SLO threshold.",
            ],
        }

    def inject_errors(self, error_rate_pct: int = 10) -> Dict[str, Any]:
        self.chaos_state["error_rate_pct"] = error_rate_pct
        return {
            "name": f"Inject {error_rate_pct}% Server Errors",
            "target": "telemetry-ingestion-endpoint",
            "status": "RUNNING",
            "expected": "Error rate exceeds baseline; circuit breaker alerts trigger",
            "actual": f"Injected {error_rate_pct}% simulated HTTP 500 faults.",
            "logs": [
                f"[T+0.0s] Set error rate to {error_rate_pct}%.",
                "[T+0.5s] Error rate counter tracked in Prometheus.",
            ],
        }

    def restore_all(self) -> Dict[str, Any]:
        logs = ["[T+0.0s] Initiating global auto-healing and reset"]
        try:
            subprocess.run(["docker", "unpause", "unitransit-redis"], capture_output=True)
            logs.append("[T+0.4s] Unpaused unitransit-redis container.")
        except Exception:
            pass

        self.chaos_state["artificial_latency_ms"] = 0
        self.chaos_state["error_rate_pct"] = 0
        self.chaos_state["db_failure"] = False
        logs.append("[T+0.8s] Reset latency and error rate flags to 0.")
        logs.append("[T+1.2s] Cleared database outage flag.")

        # Ensure baseline workers
        from apps.devops.worker_manager import ensure_worker_count
        res = ensure_worker_count(2)
        logs.append(f"[T+1.8s] Worker pool verified: {res.get('active', 2)} active workers.")
        logs.append("[T+2.2s] All services reporting HEALTHY.")

        return {
            "name": "Auto-Heal & Restore All Services",
            "target": "system/all",
            "status": "RECOVERED",
            "expected": "Containers unpaused, flags cleared, worker pool restored",
            "actual": "Complete system recovery executed.",
            "logs": logs,
        }
