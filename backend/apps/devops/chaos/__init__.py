import os
from apps.devops.chaos.base import ChaosController
from apps.devops.chaos.docker_chaos import DockerChaosController
from apps.devops.chaos.k8s_chaos import KubernetesChaosController


def get_chaos_controller(chaos_state_ref) -> ChaosController:
    """
    Factory returning the active ChaosController instance based on deployment mode.
    Defaults to DockerChaosController for local environment.
    """
    mode = os.getenv("DEPLOYMENT_MODE", "docker").lower()
    if mode == "kubernetes" or mode == "k8s":
        return KubernetesChaosController(namespace=os.getenv("K8S_NAMESPACE", "unitransit"))
    return DockerChaosController(chaos_state_ref=chaos_state_ref)
