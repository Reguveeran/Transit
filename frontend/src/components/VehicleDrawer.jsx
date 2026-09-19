import React, { useState, useEffect } from 'react';
import { X, Navigation, Gauge, Clock, Users, AlertTriangle, Compass, MapPin, Info } from 'lucide-react';

export default function VehicleDrawer({ vehicle, onClose }) {
  const [etaData, setEtaData] = useState(null);
  const [showDelayWhy, setShowDelayWhy] = useState(false);

  useEffect(() => {
    if (!vehicle?.vehicle_id) return;

    const fetchEta = async () => {
      try {
        const res = await fetch(`/api/v1/vehicles/${vehicle.vehicle_id}/eta/`);
        if (res.ok) {
          const data = await res.json();
          setEtaData(data);
        }
      } catch (err) {
        console.error('Failed to fetch vehicle ETA:', err);
      }
    };

    fetchEta();
    const interval = setInterval(fetchEta, 3000);
    return () => clearInterval(interval);
  }, [vehicle?.vehicle_id]);

  if (!vehicle) return null;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '24px',
        right: '24px',
        width: '360px',
        background: 'var(--bg-card)',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 12px 36px rgba(0,0,0,0.7)',
        backdropFilter: 'blur(16px)',
        zIndex: 1000,
        padding: '18px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h4 style={{ fontSize: '18px', fontWeight: 800, margin: 0 }}>
            {vehicle.label || vehicle.vehicle_id}
          </h4>
          <span style={{ fontSize: '11px', color: '#3b82f6', textTransform: 'uppercase', fontWeight: 700 }}>
            {vehicle.mode_name || vehicle.mode || 'Transit'}
          </span>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Dynamic Next Stop & Destination ETA */}
      {etaData && (
        <div style={{
          background: 'rgba(59, 130, 246, 0.08)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '10px',
          padding: '10px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11px', color: '#94a3b8' }}>Next Station</span>
            <strong style={{ fontSize: '13px', color: '#10b981' }}>
              in {etaData.next_stop.arrival_minutes} min
            </strong>
          </div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: 'white' }}>
            📍 {etaData.next_stop.name} ({etaData.next_stop.distance_km} km)
          </div>
          <div style={{ fontSize: '11px', color: '#64748b', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '4px' }}>
            Destination: <strong>{etaData.destination.name}</strong> • ETA: <strong>{etaData.destination.estimated_arrival}</strong>
          </div>
        </div>
      )}

      {/* Route Deviation Banner */}
      {etaData?.route_deviation && (
        <div style={{
          background: etaData.route_deviation.is_deviated ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.1)',
          border: `1px solid ${etaData.route_deviation.is_deviated ? '#ef4444' : '#10b981'}`,
          borderRadius: '8px',
          padding: '8px 10px',
          fontSize: '11px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          color: etaData.route_deviation.is_deviated ? '#fca5a5' : '#86efac',
        }}>
          <AlertTriangle size={14} />
          <span>{etaData.route_deviation.status_alert} ({etaData.route_deviation.deviation_meters}m off-track)</span>
        </div>
      )}

      {/* Telemetry Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div style={{ background: 'var(--bg-glass)', padding: '8px 10px', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <Gauge size={13} /> Current Speed
          </div>
          <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '2px' }}>
            {vehicle.current_speed || 0} km/h
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', padding: '8px 10px', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <Clock size={13} /> Schedule Delay
          </div>
          <div style={{ fontSize: '15px', fontWeight: 700, marginTop: '2px', color: (vehicle.delay_seconds || 0) > 60 ? '#ef4444' : '#10b981' }}>
            {(vehicle.delay_seconds || 0) > 60 ? `+${Math.floor(vehicle.delay_seconds / 60)} min` : 'On Time'}
          </div>
        </div>
      </div>

      {/* "Why is my transport delayed?" Root-Cause Explainer */}
      {etaData?.delay?.root_cause_explanation && (
        <div style={{
          background: 'rgba(0,0,0,0.3)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '10px',
        }}>
          <button
            onClick={() => setShowDelayWhy(!showDelayWhy)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#60a5fa',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: 0,
            }}
          >
            <Info size={13} /> Why is my transport {etaData.delay.is_delayed ? 'delayed?' : 'on time?'}
          </button>

          {showDelayWhy && (
            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {etaData.delay.root_cause_explanation.map((reason, idx) => (
                <div key={idx} style={{ fontSize: '11px', color: '#cbd5e1' }}>
                  • {reason}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
        <span>Heading: {Math.round(vehicle.current_heading || 0)}°</span>
        <span>GPS: {Number(vehicle.current_latitude || 0).toFixed(4)}, {Number(vehicle.current_longitude || 0).toFixed(4)}</span>
      </div>
    </div>
  );
}
