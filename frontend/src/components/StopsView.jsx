import React from 'react';
import { MapPin } from 'lucide-react';

export default function StopsView({ stops }) {
  return (
    <div>
      <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
        Transit Stops & Stations
      </h3>

      {stops.map((stop) => (
        <div key={stop.stop_id} className="transit-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <MapPin size={16} color="#3b82f6" />
            <strong style={{ fontSize: '14px' }}>{stop.name}</strong>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginLeft: '24px' }}>
            Station Code: <strong style={{ color: '#fff' }}>{stop.code || stop.stop_id}</strong>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '24px', marginTop: '2px' }}>
            Coord: {stop.latitude.toFixed(4)}, {stop.longitude.toFixed(4)}
          </div>
        </div>
      ))}
    </div>
  );
}
