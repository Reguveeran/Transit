# Kubernetes Manifests

Production Kubernetes manifests with Kustomize overlays for `dev` and `prod`.

## Directory Layout
- `base/`: Base manifests for `frontend`, `backend`, `workers`, `simulator`, `redis`, `postgres`, `ingress`, `hpa`, `network-policies`.
- `overlays/dev/`: Development environment customization (e.g. lightweight replica counts, local storage).
- `overlays/prod/`: Production environment customization (e.g. multi-replica HPA, high memory/CPU limits, strict ingress TLS).
