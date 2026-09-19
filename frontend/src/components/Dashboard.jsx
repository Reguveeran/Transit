import React from 'react';
import { Bus, Train, Ship, Activity, Clock, ShieldAlert } from 'lucide-react';

export default function Dashboard({ vehicles, routes, alerts, onSelectVehicle }) {
  const activeCount = vehicles.filter((v) => v.status === 'MOVING').length;
  const delayedCount = vehicles.filter((v) => (v.delay_seconds || 0) > 120).length;
  const movingVehicles = vehicles.filter((v) => v.status === 'MOVING');
  const avgSpeed = movingVehicles.length
    ? Math.round(movingVehicles.reduce((acc, v) => acc + (v.current_speed || 0), 0) / movingVehicles.length)
    : 0;

  return (
    <div>
      {/* Overview Stat Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '18px' }}>
        <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '12px' }}>
            <Activity size={14} color="#10b981" /> Active Fleet
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>
            {activeCount} <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>/ {vehicles.length}</span>
          </div>
        </div>

        <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '12px' }}>
            <Clock size={14} color="#f59e0b" /> Delayed
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px', color: delayedCount > 0 ? '#f59e0b' : '#10b981' }}>
            {delayedCount}
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-secondary)' }}>
          Live Tracking Feed
        </h3>
        <span style={{ fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span className="pulse-dot"></span> Streaming
        </span>
      </div>

      {/* Vehicle Live List */}
      <div>
        {vehicles.map((veh) => (
          <div
            key={veh.vehicle_id}
            className="transit-card"
            onClick={() => onSelectVehicle(veh)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: '15px' }}>{veh.vehicle_id}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {veh.label || `${veh.mode_name || 'Bus'} Transit`}
                </div>
              </div>
              <span className={`status-pill status-${(veh.status || 'moving').toLowerCase()}`}>
                {veh.status || 'MOVING'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '12px', color: 'var(--text-muted)' }}>
              <span>Speed: <strong style={{ color: '#f9fafb' }}>{veh.current_speed || 0} km/h</strong></span>
              <span>Delay: <strong style={{ color: (veh.delay_seconds || 0) > 60 ? '#ef4444' : '#10b981' }}>
                {(veh.delay_seconds || 0) > 0 ? `+${veh.delay_seconds}s` : 'On Time'}
              </strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
