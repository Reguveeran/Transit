from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ChaosController(ABC):
    """
    Abstract interface for chaos fault injection and self-healing recovery.
    Decouples the Operations Dashboard and SRE controllers from the underlying
    runtime environment (Local Docker vs Kubernetes).
    """

    @abstractmethod
    def disconnect_redis(self) -> Dict[str, Any]:
        """Pauses or cuts network to the Redis broker."""
        pass

    @abstractmethod
    def restore_redis(self) -> Dict[str, Any]:
        """Restores broker connectivity."""
        pass

    @abstractmethod
    def stop_worker(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        """Terminates an individual worker or all background workers."""
        pass

    @abstractmethod
    def start_worker(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        """Starts an individual worker process."""
        pass

    @abstractmethod
    def scale_workers(self, target: int) -> Dict[str, Any]:
        """Scales the worker pool to the target number of replicas."""
        pass

    @abstractmethod
    def inject_db_failure(self) -> Dict[str, Any]:
        """Simulates primary database failure or connectivity refusal."""
        pass

    @abstractmethod
    def add_latency(self, latency_ms: int = 500) -> Dict[str, Any]:
        """Injects artificial latency into API request pipeline."""
        pass

    @abstractmethod
    def inject_errors(self, error_rate_pct: int = 10) -> Dict[str, Any]:
        """Injects artificial server errors (HTTP 500) into API pipeline."""
        pass

    @abstractmethod
    def restore_all(self) -> Dict[str, Any]:
        """Restores all faulted components back to a healthy state."""
        pass
