# Kubernetes Chaos & Reliability Engineering Lab

This document defines the 9 mandatory failure testing, autoscaling, and rollback experiments for the UniTransit platform.

---

## Experiment 1: Pod Self-Healing (Delete Backend Pod)
**Objective**: Verify ReplicaSet ensures high availability when a pod abruptly dies.

```bash
# 1. Inspect running backend pods
kubectl get pods -n unitransit -l app=backend

# 2. Kill one backend pod
POD_NAME=$(kubectl get pods -n unitransit -l app=backend -o jsonpath='{.items[0].metadata.name}')
echo "Terminating pod: $POD_NAME"
kubectl delete pod $POD_NAME -n unitransit

# 3. Verify immediate recreation
kubectl get pods -n unitransit -l app=backend --watch
```
*Expected Outcome*: The deleted pod enters `Terminating` and a new replica is scheduled immediately within milliseconds, causing zero downtime for transit tracking.

---

## Experiment 2: Broken Version Deployment & Rollout Halt
**Objective**: Demonstrate how Readiness Probes prevent broken code from receiving traffic.

```bash
# 1. Update backend deployment with a broken image tag
kubectl set image deployment/backend backend=unitransit/backend:v_broken -n unitransit

# 2. Monitor rollout status
kubectl rollout status deployment/backend -n unitransit
```
*Expected Outcome*: Kubernetes fails readiness checks for the new pod and refuses to kill existing healthy pods. Traffic remains routed to healthy replicas.

---

## Experiment 3: Rollout History & Instant Rollback
**Objective**: Revert to the last known healthy revision without service disruption.

```bash
# 1. View deployment revision history
kubectl rollout history deployment/backend -n unitransit

# 2. Undo rollout to healthy revision
kubectl rollout undo deployment/backend -n unitransit

# 3. Confirm rollout status
kubectl rollout status deployment/backend -n unitransit
```
*Expected Outcome*: Deployment rolls back seamlessly to the previous stable revision.

---

## Experiment 4: High Load Induction & HPA Horizontal Scaling
**Objective**: Scale worker and backend pods automatically under heavy simulator telemetry.

```bash
# 1. Watch HPA status
kubectl get hpa -n unitransit --watch &

# 2. Scale simulator to inject high concurrent load (5,000 vehicles)
kubectl scale deployment/simulator --replicas=5 -n unitransit

# 3. Observe CPU utilization rise above 70% threshold
kubectl top pods -n unitransit
```
*Expected Outcome*: HorizontalPodAutoscaler detects CPU spike and scales backend replicas from 2 up to 10 pods, and position workers from 2 up to 8 pods.

---

## Experiment 5: Log Inspection & Forensic Troubleshooting
**Objective**: Correlate anomalies across distributed components.

```bash
# Stream backend access logs
kubectl logs -n unitransit -l app=backend -f --tail=50

# Stream position worker processing logs
kubectl logs -n unitransit -l app=worker-position -f --tail=50

# Stream alert evaluation engine logs
kubectl logs -n unitransit -l app=worker-alert -f --tail=50
```

---

## Experiment 6: Prometheus Metrics Verification
Verify scrape endpoints during chaos experiments:
```bash
# Port-forward Prometheus UI
kubectl port-forward svc/prometheus 9090:9090 -n unitransit
```
Query:
- `rate(unitransit_telemetry_events_processed_total[1m])`
- `histogram_quantile(0.95, sum(rate(unitransit_event_processing_latency_seconds_bucket[5m])) by (le))`
- `unitransit_active_vehicles`

---

## Experiment 7: Grafana Dashboard Inspection
Verify the 4 pre-configured dashboards in Grafana:
```bash
# Port-forward Grafana
kubectl port-forward svc/grafana 3001:3000 -n unitransit
```
Open `http://localhost:3001` (User: `admin`, Password: `admin`):
1. **Infrastructure**: Review container CPU & Memory during scaling.
2. **API Performance**: Verify 2xx request rate and p95 latency stays under 100ms.
3. **Transport Metrics**: Verify vehicle breakdown and alert triggers.
4. **Real-Time Pipeline**: Verify Redis stream consumption rate matches simulator throughput.
