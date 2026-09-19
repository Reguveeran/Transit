import React from 'react';
import { X, Navigation, Gauge, Clock, Users } from 'lucide-react';

export default function VehicleDrawer({ vehicle, onClose }) {
  if (!vehicle) return null;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '24px',
        right: '24px',
        width: '340px',
        background: 'var(--bg-card)',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 12px 36px rgba(0,0,0,0.6)',
        backdropFilter: 'blur(16px)',
        zIndex: 1000,
        padding: '18px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h4 style={{ fontSize: '18px', fontWeight: 800 }}>{vehicle.vehicle_id}</h4>
          <span style={{ fontSize: '12px', color: '#3b82f6', textTransform: 'uppercase', fontWeight: 700 }}>
            {vehicle.mode_name || vehicle.mode || 'Bus'}
          </span>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div style={{ background: 'var(--bg-glass)', padding: '10px', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <Gauge size={14} /> Speed
          </div>
          <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px' }}>
            {vehicle.current_speed || 0} km/h
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', padding: '10px', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <Clock size={14} /> Delay
          </div>
          <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px', color: (vehicle.delay_seconds || 0) > 60 ? '#ef4444' : '#10b981' }}>
            {(vehicle.delay_seconds || 0) > 0 ? `+${vehicle.delay_seconds}s` : 'On Time'}
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', padding: '10px', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <Navigation size={14} /> Heading
          </div>
          <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px' }}>
            {Math.round(vehicle.current_heading || 0)}°
          </div>
        </div>

        <div style={{ background: 'var(--bg-glass)', padding: '10px', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <Users size={14} /> Status
          </div>
          <div style={{ fontSize: '14px', fontWeight: 700, marginTop: '2px', textTransform: 'capitalize' }}>
            {(vehicle.status || 'MOVING').toLowerCase()}
          </div>
        </div>
      </div>

      <div style={{ marginTop: '12px', fontSize: '11px', color: 'var(--text-muted)' }}>
        GPS: {Number(vehicle.current_latitude).toFixed(4)}, {Number(vehicle.current_longitude).toFixed(4)}
      </div>
    </div>
  );
}
