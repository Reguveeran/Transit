import React, { useState, useEffect } from 'react';
import { Radio, MapPin, Route as RouteIcon, Bell, Navigation, Activity, Compass, Settings2, Sliders } from 'lucide-react';
import LiveMap from './components/LiveMap';
import Dashboard from './components/Dashboard';
import RoutesView from './components/RoutesView';
import StopsView from './components/StopsView';
import AlertsBanner from './components/AlertsBanner';
import VehicleDrawer from './components/VehicleDrawer';
import JourneyPlanner from './components/commuter/JourneyPlanner';
import NearbyTransit from './components/commuter/NearbyTransit';
import OperationsDashboard from './components/devops/OperationsDashboard';
import { useWebSocket } from './hooks/useWebSocket';

export default function App() {
  const [activeTab, setActiveTab] = useState('live');
  const [vehicles, setVehicles] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [stops, setStops] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  const { vehicleUpdates, alerts, isConnected } = useWebSocket();

  // Fetch initial REST data from backend
  useEffect(() => {
    fetch('/api/v1/vehicles/')
      .then((res) => res.json())
      .then((data) => setVehicles(data.results || data))
      .catch((err) => console.warn('Could not load vehicles REST API', err));

    fetch('/api/v1/routes/')
      .then((res) => res.json())
      .then((data) => setRoutes(data.results || data))
      .catch((err) => console.warn('Could not load routes REST API', err));

    fetch('/api/v1/stops/')
      .then((res) => res.json())
      .then((data) => setStops(data.results || data))
      .catch((err) => console.warn('Could not load stops REST API', err));
  }, []);

  // Merge incoming WebSocket updates into vehicles array
  useEffect(() => {
    if (!Object.keys(vehicleUpdates).length) return;

    setVehicles((prevVehicles) => {
      const updated = [...prevVehicles];
      Object.entries(vehicleUpdates).forEach(([vId, up]) => {
        const idx = updated.findIndex((v) => v.vehicle_id === vId);
        if (idx !== -1) {
          updated[idx] = {
            ...updated[idx],
            current_latitude: up.latitude,
            current_longitude: up.longitude,
            current_speed: up.speed,
            current_heading: up.heading,
            status: up.status,
            delay_seconds: up.delay_seconds,
          };
        } else {
          updated.push({
            vehicle_id: vId,
            mode_name: up.mode || 'bus',
            current_latitude: up.latitude,
            current_longitude: up.longitude,
            current_speed: up.speed,
            current_heading: up.heading,
            status: up.status,
            delay_seconds: up.delay_seconds,
          });
        }
      });
      return updated;
    });

    if (selectedVehicle && vehicleUpdates[selectedVehicle.vehicle_id]) {
      const up = vehicleUpdates[selectedVehicle.vehicle_id];
      setSelectedVehicle((prev) => ({
        ...prev,
        current_latitude: up.latitude,
        current_longitude: up.longitude,
        current_speed: up.speed,
        current_heading: up.heading,
        status: up.status,
        delay_seconds: up.delay_seconds,
      }));
    }
  }, [vehicleUpdates]);

  return (
    <div className="app-container">
      {/* Floating Service Alerts Banner */}
      <AlertsBanner alerts={alerts} />

      {/* Left Sidebar Controller */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-badge">
            <div className="logo-icon">U</div>
            <div>
              <div className="logo-title">UniTransit</div>
              <div className="logo-subtitle">Real-Time Platform + DevOps Lab</div>
            </div>
          </div>
          <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', color: isConnected ? '#10b981' : '#f59e0b' }}>
            <span className="pulse-dot" style={{ backgroundColor: isConnected ? '#10b981' : '#f59e0b' }}></span>
            {isConnected ? 'LIVE' : 'CONNECTING'}
          </span>
        </div>

        {/* Dual Mode Switcher Bar */}
        <div style={{
          padding: '8px 16px',
          background: 'rgba(15, 23, 42, 0.5)',
          borderBottom: '1px solid var(--border-color)',
        }}>
          <button
            onClick={() => setActiveTab(activeTab === 'operations' ? 'live' : 'operations')}
            style={{
              width: '100%',
              background: activeTab === 'operations'
                ? 'linear-gradient(135deg, #10b981, #059669)'
                : 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(16, 185, 129, 0.15))',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              borderRadius: '8px',
              padding: '8px 12px',
              color: 'white',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: activeTab === 'operations' ? '0 0 15px rgba(16, 185, 129, 0.4)' : 'none',
              transition: 'all 0.2s',
            }}
          >
            <Settings2 size={16} />
            {activeTab === 'operations' ? '← Back to Commuter Map' : '⚙️ Open DevOps Operations Lab'}
          </button>
        </div>

        {/* Commuter Navigation Tabs */}
        {activeTab !== 'operations' && (
          <div className="nav-tabs" style={{ flexWrap: 'wrap', gap: '4px' }}>
            <button
              className={`nav-tab-btn ${activeTab === 'live' ? 'active' : ''}`}
              onClick={() => setActiveTab('live')}
            >
              <Activity size={13} /> Fleet
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'routes' ? 'active' : ''}`}
              onClick={() => setActiveTab('routes')}
            >
              <RouteIcon size={13} /> Lines
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'stops' ? 'active' : ''}`}
              onClick={() => setActiveTab('stops')}
            >
              <MapPin size={13} /> Stops
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'journey' ? 'active' : ''}`}
              onClick={() => setActiveTab('journey')}
            >
              <Navigation size={13} /> Journey
            </button>
            <button
              className={`nav-tab-btn ${activeTab === 'nearby' ? 'active' : ''}`}
              onClick={() => setActiveTab('nearby')}
            >
              <Compass size={13} /> Near Me
            </button>
          </div>
        )}

        {/* Sidebar Views */}
        <div className="sidebar-content">
          {activeTab === 'live' && (
            <Dashboard
              vehicles={vehicles}
              routes={routes}
              alerts={alerts}
              onSelectVehicle={setSelectedVehicle}
            />
          )}

          {activeTab === 'routes' && <RoutesView routes={routes} />}

          {activeTab === 'stops' && <StopsView stops={stops} />}

          {activeTab === 'journey' && <JourneyPlanner onSelectJourney={setSelectedVehicle} />}

          {activeTab === 'nearby' && <NearbyTransit onSelectVehicle={setSelectedVehicle} />}

          {activeTab === 'operations' && (
            <div style={{ fontSize: '13px', color: '#94a3b8', lineHeight: '1.6' }}>
              <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px', marginBottom: '12px', color: '#6ee7b7' }}>
                <strong>DevOps Lab Active</strong>
                <p style={{ margin: '4px 0 0', fontSize: '11px', color: '#a7f3d0' }}>
                  The main viewport has switched from the commuter map to the real-time SRE & Operations command center.
                </p>
              </div>
              <p>Explore real-time infrastructure capabilities:</p>
              <ul style={{ paddingLeft: '18px', margin: '8px 0' }}>
                <li>🩺 System Health & Redis lag</li>
                <li>🕸️ Service Dependency Topology</li>
                <li>🔥 Chaos Engineering Lab</li>
                <li>🧪 Load Testing & HPA Scaling</li>
                <li>🚀 Canary Deployment & Rollback</li>
                <li>🚨 SRE Incidents & Postmortems</li>
                <li>🔍 Structured Log Explorer</li>
                <li>🎯 Service Level Objectives (SLOs)</li>
                <li>⚡ Zero-Downtime Feature Flags</li>
              </ul>
            </div>
          )}
        </div>
      </aside>

      {/* Main Viewport: Either Live Map OR DevOps Operations Dashboard */}
      <main className="map-viewport" style={{ position: 'relative', width: '100%', height: '100%' }}>
        {activeTab === 'operations' ? (
          <OperationsDashboard />
        ) : (
          <>
            <LiveMap
              vehicles={vehicles}
              routes={routes}
              stops={stops}
              selectedVehicle={selectedVehicle}
              onSelectVehicle={setSelectedVehicle}
            />

            {/* Inspector Drawer */}
            <VehicleDrawer
              vehicle={selectedVehicle}
              onClose={() => setSelectedVehicle(null)}
            />
          </>
        )}
      </main>
    </div>
  );
}
