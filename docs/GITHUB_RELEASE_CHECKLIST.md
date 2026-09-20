# UniTransit GitHub Release Checklist

Use this checklist prior to committing or tagging releases on GitHub:

- [x] **README Complete**: Comprehensive 29-section portfolio README with Mermaid diagrams, pipeline details, and architecture.
- [x] **Architecture Documented**: Full cloud and local architecture diagrams (`docs/AWS_ARCHITECTURE.md`).
- [x] **DevOps Journey Documented**: Step-by-step evolution from telemetry ingest to cloud architecture (`docs/DEVOPS_JOURNEY.md`).
- [x] **Project Status Clear**: Explicit distinction that AWS architecture is declarative and NOT provisioned in AWS (`docs/PROJECT_STATUS.md`).
- [x] **Secrets & Credentials Audit**: Automated audit confirmed zero private keys, API keys, or tokens in repository.
- [x] **.gitignore Verified**: Correctly ignores `.env`, `*.tfvars`, `*.tfstate`, `build/`, `.venv/`, and `.terraform/` while tracking `.terraform.lock.hcl`.
- [x] **Terraform Examples Provided**: Clean `terraform.tfvars.example` files created across all local and AWS environments.
- [x] **Automated Tests Passing**: 77/77 tests passing (`OK`).
- [x] **Terraform Validation**: `terraform fmt` and `terraform validate` passing across all 6 environments.
- [x] **Local Kubernetes Preserved**: All 22 pods active across `unitransit-dev` (8/8), `unitransit-iac` (8/8), and `unitransit` (6/6).
- [x] **CI/CD Supply Chain Workflows**: GitHub Actions workflows verified for automated tests, Trivy scanning, and GHCR publishing.
