import React, { useState, useEffect } from 'react';
import {
  Activity, Server, Database, Radio, Flame, Cpu, GitCommit,
  AlertTriangle, Terminal, Target, ToggleLeft, ToggleRight, Play, RefreshCw, CheckCircle2, ShieldAlert
} from 'lucide-react';

export default function OperationsDashboard() {
  const [activeTab, setActiveTab] = useState('health');
  const [healthData, setHealthData] = useState(null);
  const [serviceGraph, setServiceGraph] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [chaosLog, setChaosLog] = useState([]);
  const [isChaosRunning, setIsChaosRunning] = useState(false);
  const [activeExperiment, setActiveExperiment] = useState(null);
  const [loadResult, setLoadResult] = useState(null);
  const [loadVehicles, setLoadVehicles] = useState(2500);
  const [isLoadTesting, setIsLoadTesting] = useState(false);
  const [deployments, setDeployments] = useState(null);
  const [canarySplit, setCanarySplit] = useState(10);
  const [incidents, setIncidents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [logFilter, setLogFilter] = useState('ALL');
  const [slos, setSlos] = useState(null);
  const [featureFlags, setFeatureFlags] = useState([]);

  // Fetch live health periodically
  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/v1/devops/health/');
      const data = await res.json();
      setHealthData(data);
    } catch (e) {
      console.error('Health fetch error:', e);
    }
  };

  const fetchServiceGraph = async () => {
    try {
      const res = await fetch('/api/v1/devops/service-graph/');
      const data = await res.json();
      setServiceGraph(data);
    } catch (e) {
      console.error('Service graph fetch error:', e);
    }
  };

  const fetchDeployments = async () => {
    try {
      const res = await fetch('/api/v1/devops/deployments/');
      const data = await res.json();
      setDeployments(data);
      if (data.canary_traffic) {
        setCanarySplit(data.canary_traffic.canary_traffic_pct);
      }
    } catch (e) {
      console.error('Deployments fetch error:', e);
    }
  };

  const fetchIncidents = async () => {
    try {
      const res = await fetch('/api/v1/devops/incidents/');
      const data = await res.json();
      setIncidents(data.incidents || []);
    } catch (e) {
      console.error('Incidents fetch error:', e);
    }
  };

  const fetchLogs = async (level = 'ALL') => {
    try {
      const res = await fetch(`/api/v1/devops/logs/?level=${level}`);
      const data = await res.json();
      setLogs(data.logs || []);
    } catch (e) {
      console.error('Logs fetch error:', e);
    }
  };

  const fetchSlos = async () => {
    try {
      const res = await fetch('/api/v1/devops/slo/');
      const data = await res.json();
      setSlos(data);
    } catch (e) {
      console.error('SLOs fetch error:', e);
    }
  };

  const fetchFlags = async () => {
    try {
      const res = await fetch('/api/v1/devops/feature-flags/');
      const data = await res.json();
      setFeatureFlags(data.flags || []);
    } catch (e) {
      console.error('Flags fetch error:', e);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchServiceGraph();
    fetchDeployments();
    fetchIncidents();
    fetchLogs(logFilter);
    fetchSlos();
    fetchFlags();

    const interval = setInterval(() => {
      fetchHealth();
      fetchLogs(logFilter);
    }, 4000);
    return () => clearInterval(interval);
  }, [logFilter]);

  // Chaos runner
  const triggerChaos = async (action) => {
    setIsChaosRunning(true);
    setActiveExperiment(null);
    try {
      const res = await fetch('/api/v1/devops/chaos/trigger/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      const data = await res.json();
      setActiveExperiment(data);
      fetchHealth();
    } catch (err) {
      console.error('Chaos trigger error:', err);
    } finally {
      setIsChaosRunning(false);
    }
  };

  // Load test runner
  const runLoadTest = async () => {
    setIsLoadTesting(true);
    try {
      const res = await fetch('/api/v1/devops/loadtest/run/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vehicles: loadVehicles, duration_sec: 15 }),
      });
      const data = await res.json();
      setLoadResult(data);
      fetchHealth();
    } catch (err) {
      console.error('Load test error:', err);
    } finally {
      setIsLoadTesting(false);
    }
  };

  // Canary adjustments
  const updateCanary = async (action, splitVal) => {
    try {
      const res = await fetch('/api/v1/devops/deployments/canary/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, split_pct: splitVal }),
      });
      const data = await res.json();
      setCanarySplit(data.canary_split_pct);
      fetchDeployments();
    } catch (err) {
      console.error('Canary update error:', err);
    }
  };

  // Toggle feature flag
  const toggleFlag = async (key, currentVal) => {
    try {
      await fetch('/api/v1/devops/feature-flags/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, is_enabled: !currentVal }),
      });
      fetchFlags();
    } catch (err) {
      console.error('Flag toggle error:', err);
    }
  };

  const navItems = [
    { id: 'health', label: 'System Health', icon: Activity },
    { id: 'graph', label: 'Service Graph', icon: Server },
    { id: 'chaos', label: 'Chaos Lab 🔥', icon: Flame },
    { id: 'load', label: 'Load & HPA 🧪', icon: Cpu },
    { id: 'deploy', label: 'Deployments 🚀', icon: GitCommit },
    { id: 'incidents', label: 'Incidents 🚨', icon: AlertTriangle },
    { id: 'logs', label: 'Logs 🔍', icon: Terminal },
    { id: 'slo', label: 'SLO / SRE 🎯', icon: Target },
    { id: 'flags', label: 'Feature Flags ⚡', icon: ToggleRight },
  ];

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-primary)',
      color: 'white',
      overflow: 'hidden',
    }}>
      {/* Top DevOps Header */}
      <div style={{
        padding: '12px 20px',
        background: 'rgba(15, 23, 42, 0.95)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backdropFilter: 'blur(10px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #10b981, #3b82f6)',
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
          }}>
            ⚙
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700 }}>
              UniTransit DevOps Operations Platform
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              Environment: <span style={{ color: '#10b981', fontWeight: 600 }}>Production (Active)</span> • Commit: <code>{deployments?.active_commit?.sha || 'fd86469'}</code>
            </div>
          </div>
        </div>

        {/* Live Metrics Quick Badges */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '4px 10px', borderRadius: '6px', fontSize: '11px' }}>
            Throughput: <strong style={{ color: '#60a5fa' }}>{healthData?.telemetry_rates?.events_ingested_per_sec || 1248} evt/s</strong>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '4px 10px', borderRadius: '6px', fontSize: '11px' }}>
            Latency: <strong style={{ color: '#10b981' }}>{healthData?.telemetry_rates?.api_p95_latency_ms || 78}ms</strong>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '4px 10px', borderRadius: '6px', fontSize: '11px' }}>
            HPA Pods: <strong style={{ color: '#a855f7' }}>{healthData?.telemetry_rates?.active_pods || 3} Replicas</strong>
          </div>
          <button
            onClick={() => { fetchHealth(); fetchLogs(logFilter); }}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
            title="Refresh Metrics"
          >
            <RefreshCw size={15} />
          </button>
        </div>
      </div>

      {/* Sub-Navigation Bar */}
      <div style={{
        display: 'flex',
        gap: '4px',
        padding: '8px 16px',
        background: 'rgba(15, 23, 42, 0.7)',
        borderBottom: '1px solid var(--border-color)',
        overflowX: 'auto',
      }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                background: isActive ? '#2563eb' : 'transparent',
                color: isActive ? 'white' : '#94a3b8',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s',
              }}
            >
              <Icon size={14} />
              {item.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
        {/* 1. SYSTEM HEALTH TAB */}
        {activeTab === 'health' && healthData && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Health Matrix Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {/* API Service */}
              <div className="transit-card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>API Gateway & WS</span>
                  <span className="status-pill status-moving">● {healthData.services.api_server.status}</span>
                </div>
                <div style={{ fontSize: '24px', fontWeight: 700, margin: '10px 0 4px', color: 'white' }}>
                  {healthData.services.api_server.latency_ms} ms
                </div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Requests/sec: {healthData.telemetry_rates.requests_per_sec} • Subscriptions: {healthData.services.websocket_hub.active_subscribers}
                </div>
              </div>

              {/* Redis Streams */}
              <div className="transit-card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Redis Streams Broker</span>
                  <span className="status-pill status-moving">● {healthData.services.redis_stream.status}</span>
                </div>
                <div style={{ fontSize: '24px', fontWeight: 700, margin: '10px 0 4px', color: '#10b981' }}>
                  {healthData.services.redis_stream.consumer_lag_sec}s <span style={{ fontSize: '14px', fontWeight: 400, color: '#94a3b8' }}>lag</span>
                </div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Memory: {healthData.services.redis_stream.used_memory_human} • {healthData.services.redis_stream.ops_per_sec} ops/s
                </div>
              </div>

              {/* PostgreSQL */}
              <div className="transit-card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Database Engine</span>
                  <span className="status-pill status-moving">● {healthData.services.database.status}</span>
                </div>
                <div style={{ fontSize: '24px', fontWeight: 700, margin: '10px 0 4px', color: 'white' }}>
                  {healthData.services.database.latency_ms} ms
                </div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Engine: {healthData.services.database.type} • Fleet Records: {healthData.services.simulator.fleet_size}
                </div>
              </div>

              {/* Ingestion Pipeline */}
              <div className="transit-card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Multi-Modal Ingestion</span>
                  <span className="status-pill status-moving">● ACTIVE</span>
                </div>
                <div style={{ fontSize: '24px', fontWeight: 700, margin: '10px 0 4px', color: '#60a5fa' }}>
                  {healthData.telemetry_rates.events_ingested_per_sec} <span style={{ fontSize: '14px', fontWeight: 400, color: '#94a3b8' }}>evt/sec</span>
                </div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Active Moving Fleet: {healthData.services.simulator.active_moving} • Error Rate: {healthData.telemetry_rates.error_rate_pct}%
                </div>
              </div>
            </div>

            {/* Live Prometheus Rate Metrics Box */}
            <div style={{
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '18px',
            }}>
              <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 700 }}>
                Real-Time Prometheus & Node Exporter Telemetry
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>HTTP P95 Response Latency</div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#38bdf8' }}>{healthData.telemetry_rates.api_p95_latency_ms} ms</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>Cluster Auto-Scaled Pods</div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#a855f7' }}>{healthData.telemetry_rates.active_pods} Pods</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>Process Uptime</div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#10b981' }}>{Math.floor(healthData.uptime_seconds / 60)} min {healthData.uptime_seconds % 60}s</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>HTTP Error Rate</div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: healthData.telemetry_rates.error_rate_pct > 1 ? '#ef4444' : '#10b981' }}>
                    {healthData.telemetry_rates.error_rate_pct}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 2. SERVICE DEPENDENCY GRAPH TAB */}
        {activeTab === 'graph' && serviceGraph && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
              Interactive architecture topology map. Click any node to inspect live dependencies, protocol, and throughput.
            </div>

            {/* Architecture Node Canvas */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '14px',
            }}>
              {serviceGraph.nodes.map((node) => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  style={{
                    background: selectedNode?.id === node.id ? 'rgba(59, 130, 246, 0.2)' : 'var(--bg-card)',
                    border: selectedNode?.id === node.id ? '2px solid #3b82f6' : '1px solid var(--border-color)',
                    borderRadius: '12px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', color: '#60a5fa', fontWeight: 700 }}>
                      {node.category}
                    </span>
                    <span style={{ fontSize: '11px', color: '#10b981', fontWeight: 600 }}>
                      ● {node.status}
                    </span>
                  </div>
                  <h4 style={{ margin: '8px 0 4px', fontSize: '14px', fontWeight: 700, color: 'white' }}>
                    {node.name}
                  </h4>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>
                    {Object.entries(node.metrics || {}).map(([k, v]) => (
                      <span key={k} style={{ marginRight: '8px' }}>
                        {k}: <strong>{v}</strong>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Inspector Modal for Selected Node */}
            {selectedNode && (
              <div style={{
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #3b82f6',
                borderRadius: '12px',
                padding: '16px',
                marginTop: '10px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, fontSize: '15px', color: '#60a5fa' }}>
                    Node Inspector: {selectedNode.name}
                  </h4>
                  <button onClick={() => setSelectedNode(null)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>✕</button>
                </div>
                <div style={{ display: 'flex', gap: '20px', marginTop: '12px', flexWrap: 'wrap' }}>
                  <div>Category: <strong>{selectedNode.category}</strong></div>
                  <div>Health: <strong style={{ color: '#10b981' }}>{selectedNode.status}</strong></div>
                  {Object.entries(selectedNode.metrics || {}).map(([k, v]) => (
                    <div key={k}>{k}: <strong style={{ color: '#38bdf8' }}>{v}</strong></div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 3. CHAOS LAB TAB */}
        {activeTab === 'chaos' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: '18px', fontWeight: 700 }}>
                Chaos Engineering Lab 🔥
              </h3>
              <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                Deliberately inject failures into the running architecture to test Kubernetes replica recovery, circuit breaking, and auto-failover.
              </p>
            </div>

            {/* Chaos Trigger Buttons Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
              <button
                onClick={() => triggerChaos('kill_api_pod')}
                disabled={isChaosRunning}
                style={{
                  background: 'linear-gradient(135deg, #ef4444, #b91c1c)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '14px',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>💥 Kill API Pod</div>
                <div style={{ fontSize: '10px', opacity: 0.8, marginTop: '4px' }}>Tests Kubernetes ReplicaSet recreation</div>
              </button>

              <button
                onClick={() => triggerChaos('stop_redis')}
                disabled={isChaosRunning}
                style={{
                  background: 'linear-gradient(135deg, #f97316, #c2410c)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '14px',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>🔌 Partition Redis</div>
                <div style={{ fontSize: '10px', opacity: 0.8, marginTop: '4px' }}>Tests fallback to memory layer</div>
              </button>

              <button
                onClick={() => triggerChaos('add_latency')}
                disabled={isChaosRunning}
                style={{
                  background: 'linear-gradient(135deg, #eab308, #a16207)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '14px',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>⏱️ Inject 500ms Latency</div>
                <div style={{ fontSize: '10px', opacity: 0.8, marginTop: '4px' }}>Tests SLA timeout and p95 degradation</div>
              </button>

              <button
                onClick={() => triggerChaos('kill_worker')}
                disabled={isChaosRunning}
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '14px',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>⚡ Kill Worker Process</div>
                <div style={{ fontSize: '10px', opacity: 0.8, marginTop: '4px' }}>Tests process supervisor respawn</div>
              </button>

              <button
                onClick={() => triggerChaos('inject_errors')}
                disabled={isChaosRunning}
                style={{
                  background: 'linear-gradient(135deg, #ec4899, #be185d)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '14px',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '13px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>⚠️ Inject 5% HTTP 500s</div>
                <div style={{ fontSize: '10px', opacity: 0.8, marginTop: '4px' }}>Tests client retry and circuit breaker</div>
              </button>
            </div>

            {/* Experiment Results Card */}
            {activeExperiment && (
              <div style={{
                background: 'rgba(15, 23, 42, 0.85)',
                border: '1px solid #10b981',
                borderRadius: '12px',
                padding: '18px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 color="#10b981" size={20} />
                    <h4 style={{ margin: 0, fontSize: '16px', color: 'white' }}>
                      Experiment: {activeExperiment.name}
                    </h4>
                  </div>
                  <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 700 }}>
                    🟢 {activeExperiment.result}
                  </span>
                </div>

                <div style={{ margin: '14px 0', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div>Target: <code>{activeExperiment.target}</code></div>
                  <div>Expected: <span style={{ color: '#94a3b8' }}>{activeExperiment.expected_behavior}</span></div>
                  <div>Actual: <strong style={{ color: '#60a5fa' }}>{activeExperiment.actual_behavior}</strong></div>
                  <div>Recovery Duration: <strong style={{ color: '#10b981' }}>{activeExperiment.recovery_time_seconds} seconds</strong></div>
                </div>

                {/* Log steps */}
                <div style={{ background: '#020617', borderRadius: '8px', padding: '10px', fontFamily: 'monospace', fontSize: '11px' }}>
                  {activeExperiment.logs?.map((l, i) => (
                    <div key={i} style={{ color: '#38bdf8', padding: '2px 0' }}>{l}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 4. LOAD TESTING & HPA TAB */}
        {activeTab === 'load' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: '18px', fontWeight: 700 }}>
                High-Throughput Load Testing & HPA Visualizer 🧪
              </h3>
              <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                Stress test the ingestion pipeline up to 10,000 concurrent vehicles and observe Kubernetes Horizontal Pod Autoscaling (HPA) in real time.
              </p>
            </div>

            {/* Slider & Start */}
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '18px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600 }}>Simulated Active Fleet Size:</label>
                  <strong style={{ color: '#60a5fa' }}>{loadVehicles.toLocaleString()} Vehicles</strong>
                </div>
                <input
                  type="range"
                  min="500"
                  max="10000"
                  step="500"
                  value={loadVehicles}
                  onChange={(e) => setLoadVehicles(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#3b82f6' }}
                />
              </div>

              <button
                onClick={runLoadTest}
                disabled={isLoadTesting}
                style={{
                  background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px',
                  fontSize: '13px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                }}
              >
                <Play size={16} />
                {isLoadTesting ? 'Injecting Telemetry Load...' : 'START LOAD TEST'}
              </button>
            </div>

            {/* Before vs After Table */}
            {loadResult && (
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '18px',
              }}>
                <h4 style={{ margin: '0 0 14px', fontSize: '15px', fontWeight: 700 }}>
                  Infrastructure Scaling Response (Before vs After)
                </h4>

                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: '#94a3b8' }}>
                      <th style={{ padding: '8px' }}>Metric</th>
                      <th style={{ padding: '8px' }}>Baseline (Before)</th>
                      <th style={{ padding: '8px' }}>Peak Load (After)</th>
                      <th style={{ padding: '8px' }}>Delta Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '10px 8px' }}>Events / sec</td>
                      <td style={{ padding: '10px 8px' }}>{loadResult.before.events_per_sec}</td>
                      <td style={{ padding: '10px 8px', color: '#10b981', fontWeight: 700 }}>{loadResult.after.events_per_sec}</td>
                      <td style={{ padding: '10px 8px', color: '#10b981' }}>+{(loadResult.after.events_per_sec - loadResult.before.events_per_sec).toLocaleString()} evt/s</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '10px 8px' }}>API Latency</td>
                      <td style={{ padding: '10px 8px' }}>{loadResult.before.api_latency_ms} ms</td>
                      <td style={{ padding: '10px 8px', color: '#f59e0b', fontWeight: 700 }}>{loadResult.after.api_latency_ms} ms</td>
                      <td style={{ padding: '10px 8px', color: '#f59e0b' }}>+{loadResult.after.api_latency_ms - loadResult.before.api_latency_ms} ms</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '10px 8px' }}>Cluster CPU</td>
                      <td style={{ padding: '10px 8px' }}>{loadResult.before.cpu_usage_pct}%</td>
                      <td style={{ padding: '10px 8px', color: '#ef4444', fontWeight: 700 }}>{loadResult.after.cpu_usage_pct}%</td>
                      <td style={{ padding: '10px 8px', color: '#ef4444' }}>+{loadResult.after.cpu_usage_pct - loadResult.before.cpu_usage_pct}%</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px 8px' }}>Kubernetes Replicas</td>
                      <td style={{ padding: '10px 8px' }}>{loadResult.before.active_pods} Pods</td>
                      <td style={{ padding: '10px 8px', color: '#a855f7', fontWeight: 700 }}>{loadResult.after.active_pods} Pods</td>
                      <td style={{ padding: '10px 8px', color: '#a855f7' }}>Auto-scaled {loadResult.before.active_pods} → {loadResult.after.active_pods}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* 5. DEPLOYMENTS & CANARY TAB */}
        {activeTab === 'deploy' && deployments && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: '18px', fontWeight: 700 }}>
                Deployment Center & Canary Releases 🚀
              </h3>
              <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                Manage live blue-green traffic splits and trigger instantaneous zero-downtime rollbacks upon telemetry anomalies.
              </p>
            </div>

            {/* Canary Split Visualizer */}
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '18px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}>
              <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 700 }}>
                Active Canary Split: v1.8.2 (Stable) vs v1.9.0-rc1 (Canary)
              </h4>

              {/* Traffic progress bar */}
              <div style={{
                height: '24px',
                borderRadius: '6px',
                background: '#1e293b',
                display: 'flex',
                overflow: 'hidden',
                fontWeight: 700,
                fontSize: '11px',
                lineHeight: '24px',
                textAlign: 'center',
              }}>
                <div style={{ width: `${100 - canarySplit}%`, background: '#2563eb', color: 'white' }}>
                  Stable v1.8.2 ({100 - canarySplit}%)
                </div>
                {canarySplit > 0 && (
                  <div style={{ width: `${canarySplit}%`, background: '#10b981', color: 'white' }}>
                    Canary ({canarySplit}%)
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => updateCanary('promote')}
                  style={{
                    background: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 14px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Promote Canary (+25%)
                </button>
                <button
                  onClick={() => updateCanary('rollback')}
                  style={{
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 14px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Emergency Rollback to v1.8.2
                </button>
              </div>
            </div>

            {/* Real Git Commit History */}
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '18px',
            }}>
              <h4 style={{ margin: '0 0 12px', fontSize: '15px', fontWeight: 700 }}>
                Recent Git Production Deployments
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {deployments.commit_history?.map((c) => (
                  <div
                    key={c.sha}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '10px 12px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <code style={{ background: '#3b82f6', color: 'white', padding: '2px 6px', borderRadius: '4px', fontSize: '11px' }}>
                        {c.sha}
                      </code>
                      <span style={{ color: 'white', fontWeight: 600 }}>{c.message}</span>
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '11px' }}>
                      {c.author} • {c.time}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 6. INCIDENTS TAB */}
        {activeTab === 'incidents' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: '18px', fontWeight: 700 }}>
                SRE Incident Management Center 🚨
              </h3>
              <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                Live postmortems, alert correlations, and incident escalation timelines.
              </p>
            </div>

            {incidents.map((inc) => (
              <div
                key={inc.id}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ background: '#ef4444', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      {inc.id}
                    </span>
                    <h4 style={{ margin: 0, fontSize: '16px', color: 'white' }}>{inc.title}</h4>
                  </div>
                  <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', padding: '3px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600 }}>
                    ● {inc.status}
                  </span>
                </div>

                <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                  Affected Subsystem: <strong>{inc.affected_service}</strong>
                </div>

                {/* Timeline */}
                <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#60a5fa', marginBottom: '8px' }}>
                    Automated SRE Timeline
                  </div>
                  {inc.timeline?.map((t, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '12px', fontSize: '12px', padding: '3px 0' }}>
                      <code style={{ color: '#f59e0b' }}>{t.time}</code>
                      <span style={{ color: '#e2e8f0' }}>{t.event}</span>
                    </div>
                  ))}
                </div>

                {/* Postmortem */}
                {inc.postmortem && (
                  <div style={{ fontSize: '12px', color: '#cbd5e1', borderLeft: '3px solid #10b981', paddingLeft: '10px' }}>
                    <strong>Postmortem:</strong> {inc.postmortem}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* 7. LOGS TAB */}
        {activeTab === 'logs' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Centralized Log Explorer 🔍</h3>
              <div style={{ display: 'flex', gap: '6px' }}>
                {['ALL', 'INFO', 'WARN', 'ERROR'].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setLogFilter(lvl)}
                    style={{
                      background: logFilter === lvl ? '#3b82f6' : 'rgba(255,255,255,0.05)',
                      color: logFilter === lvl ? 'white' : '#94a3b8',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '4px 10px',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <div style={{
              background: '#020617',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '14px',
              fontFamily: 'monospace',
              fontSize: '12px',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
              maxHeight: '460px',
              overflowY: 'auto',
            }}>
              {logs.map((l, i) => (
                <div key={i} style={{ display: 'flex', gap: '10px' }}>
                  <span style={{ color: '#64748b' }}>{l.timestamp}</span>
                  <span style={{
                    color: l.level === 'ERROR' ? '#ef4444' : l.level === 'WARN' ? '#f59e0b' : '#38bdf8',
                    fontWeight: 700,
                    minWidth: '45px',
                  }}>
                    {l.level}
                  </span>
                  <span style={{ color: '#a855f7' }}>[{l.service}]</span>
                  <span style={{ color: '#e2e8f0' }}>{l.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 8. SLO & RELIABILITY TAB */}
        {activeTab === 'slo' && slos && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: '18px', fontWeight: 700 }}>
                Service Level Objectives (SLO) & Error Budgets 🎯
              </h3>
              <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                Track live measured reliability against contractual service level agreements.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {Object.entries(slos.slo_targets || {}).map(([k, slo]) => (
                <div key={k} className="transit-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>{slo.name}</span>
                    <span style={{ color: '#10b981', fontSize: '11px', fontWeight: 700 }}>
                      ● {slo.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: 700, margin: '8px 0 4px', color: 'white' }}>
                    {slo.measured_pct ? `${slo.measured_pct}%` : `${slo.measured_ms} ms`}
                  </div>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>
                    Target: {slo.target_pct ? `${slo.target_pct}%` : `< ${slo.target_ms} ms`}
                  </div>

                  {/* Error budget bar */}
                  <div style={{ marginTop: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>
                      <span>Error Budget Remaining</span>
                      <strong>{slo.error_budget_remaining_pct}%</strong>
                    </div>
                    <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${slo.error_budget_remaining_pct}%`, height: '100%', background: '#10b981' }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 9. FEATURE FLAGS TAB */}
        {activeTab === 'flags' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: '18px', fontWeight: 700 }}>
                Runtime Feature Flags ⚡
              </h3>
              <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                Toggle features on and off dynamically across the application without rebuilding or restarting backend pods.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {featureFlags.map((flag) => (
                <div
                  key={flag.key}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '10px',
                    padding: '14px 18px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'white' }}>
                      {flag.display_name}
                    </div>
                    <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                      {flag.description} • <code>{flag.key}</code>
                    </div>
                  </div>

                  <button
                    onClick={() => toggleFlag(flag.key, flag.is_enabled)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      color: flag.is_enabled ? '#10b981' : '#64748b',
                    }}
                  >
                    {flag.is_enabled ? <ToggleRight size={32} /> : <ToggleLeft size={32} />}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
