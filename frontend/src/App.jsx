import React, { useState, useEffect } from 'react';
import { Radio, MapPin, Route as RouteIcon, Bell, Navigation, Activity } from 'lucide-react';
import LiveMap from './components/LiveMap';
import Dashboard from './components/Dashboard';
import RoutesView from './components/RoutesView';
import StopsView from './components/StopsView';
import AlertsBanner from './components/AlertsBanner';
import VehicleDrawer from './components/VehicleDrawer';
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

    // Update selected vehicle in real-time if currently opened
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
              <div className="logo-subtitle">Real-Time Multi-Transport</div>
            </div>
          </div>
          <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', color: isConnected ? '#10b981' : '#f59e0b' }}>
            <span className="pulse-dot" style={{ backgroundColor: isConnected ? '#10b981' : '#f59e0b' }}></span>
            {isConnected ? 'LIVE' : 'CONNECTING'}
          </span>
        </div>

        {/* Navigation Tabs */}
        <div className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'live' ? 'active' : ''}`}
            onClick={() => setActiveTab('live')}
          >
            <Activity size={14} /> Fleet
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'routes' ? 'active' : ''}`}
            onClick={() => setActiveTab('routes')}
          >
            <RouteIcon size={14} /> Lines
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'stops' ? 'active' : ''}`}
            onClick={() => setActiveTab('stops')}
          >
            <MapPin size={14} /> Stops
          </button>
        </div>

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
        </div>
      </aside>

      {/* Main Interactive Map Viewport */}
      <main className="map-viewport">
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
      </main>
    </div>
  );
}
