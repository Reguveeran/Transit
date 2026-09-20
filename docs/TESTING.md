# UniTransit Test Engineering & Quality Assurance

UniTransit maintains a **77-test automated regression suite** spanning unit, integration, spatial PostGIS, streaming worker, and DevOps SLO capabilities.

---

## 1. Test Execution

Execute the entire test suite locally:
```bash
PYTHONPATH=backend:. .venv/bin/python backend/manage.py test tests
```

### Verified Test Run Output:
```text
Found 77 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.............................................................................
----------------------------------------------------------------------
Ran 77 tests in 30.730s

OK
Destroying test database for alias 'default'...
```

---

## 2. Test Coverage & Functional Subsystems

### A. Real-Time Telemetry Ingestion & Stream Processing
- **Event Validation**: Schema enforcement, field typing, and ISO timestamp normalization (`test_event_schema.py`).
- **Redis Stream Broker**: High-throughput event ingestion, consumer group dispatch, and Redis connection retry loops (`test_redis_pipeline.py`).
- **PositionWorker Reliability**:
  - Acknowledgment (`XACK`) verification
  - Poison-pill error isolation and dead-letter quarantine
  - Pending Entry List (PEL) reclamation and `XAUTOCLAIM` failover recovery
- **Simulator & Load Testing**: Simulated vehicle fleet ingestion (up to 1,500 active vehicles, 10,000 evt/sec dry-run benchmark).

### B. Spatial PostGIS & Transit Entities
- **Stops & Routes**: GeoJSON `LineString` generation, geometry validation, and stop ordering.
- **Spatial Calculations**: Haversine distance computations and route proximity evaluation.
- **Tracking & Real-Time Broadcast**: Timeseries position persistence and WebSocket notification broadcasting.

### C. DevOps, SLO & Canary Engines
- **SLO Engine**: Error budget calculations, p95/p99 latency evaluations, and burn rate threshold alerting (`test_slo_engine.py`).
- **Canary Engine**: Multi-step traffic shifting validation (10% -> 50% -> 100%) and automated rollback triggers on error rate breaches.
- **Chaos & Fault Injection**: Worker crash simulation, dropped database connections, and malformed payload resilience.
- **DevOps Endpoints**: Verification of `/health`, `/ready`, `/metrics`, and operations dashboard APIs (`test_devops_endpoints.py`).

---

## 3. Continuous Integration Quality Gates
Every push and pull request executes:
1. Python 3.11 test suite (77/77 tests)
2. Flake8 syntax and linting verification
3. React / Vite production bundle compilation
4. Docker Buildx container compilation & Trivy vulnerability scan
