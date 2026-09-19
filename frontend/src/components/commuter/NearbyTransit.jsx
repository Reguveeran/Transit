import React, { useState, useEffect } from 'react';
import { Radar, Navigation, Clock, MapPin, Compass } from 'lucide-react';

export default function NearbyTransit({ onSelectVehicle }) {
  const [data, setData] = useState({ vehicles: [], stops: [] });
  const [loading, setLoading] = useState(true);

  const fetchNearby = async () => {
    try {
      const res = await fetch('/api/v1/vehicles/nearby/?lat=12.9900&lon=80.2400');
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error('Failed to fetch nearby transit:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNearby();
    const interval = setInterval(fetchNearby, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* Radar Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(59, 130, 246, 0.1))',
        border: '1px solid rgba(16, 185, 129, 0.25)',
        borderRadius: '12px',
        padding: '14px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '50%',
          background: 'rgba(16, 185, 129, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#10b981',
        }}>
          <Radar size={20} className="pulse-dot" style={{ background: 'transparent' }} />
        </div>
        <div>
          <h4 style={{ margin: 0, fontSize: '14px', fontWeight: 700, color: 'white' }}>
            Live Proximity Radar
          </h4>
          <span style={{ fontSize: '11px', color: '#94a3b8' }}>
            Tracking arrivals within 5 km of your location
          </span>
        </div>
      </div>

      {/* Nearby Vehicles */}
      <div>
        <h5 style={{ margin: '0 0 8px', fontSize: '11px', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
          Approaching Vehicles
        </h5>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {data.vehicles?.slice(0, 6).map((v) => (
            <div
              key={v.vehicle_id}
              onClick={() => onSelectVehicle && onSelectVehicle(v)}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '20px' }}>
                  {v.mode === 'aircraft' ? '✈️' : v.mode === 'ferry' ? '🚢' : v.mode === 'metro' ? '🚇' : '🚌'}
                </span>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <strong style={{ fontSize: '13px', color: 'white' }}>{v.label || v.vehicle_id}</strong>
                    <span style={{ fontSize: '10px', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', padding: '1px 6px', borderRadius: '4px' }}>
                      {v.route}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                    {v.distance_meters}m away • {v.current_speed} km/h
                  </div>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#10b981' }}>
                  in {v.eta_minutes} min
                </div>
                <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'capitalize' }}>
                  {v.status?.toLowerCase()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Nearby Stations */}
      <div style={{ marginTop: '6px' }}>
        <h5 style={{ margin: '0 0 8px', fontSize: '11px', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
          Walking Distance Stations
        </h5>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {data.stops?.slice(0, 3).map((s) => (
            <div
              key={s.stop_id}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '10px 12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MapPin size={14} color="#3b82f6" />
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'white' }}>{s.name}</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>{s.code} • {s.distance_meters}m</div>
                </div>
              </div>
              <div style={{ fontSize: '11px', fontWeight: 600, color: '#94a3b8' }}>
                🚶 {s.walk_minutes} min walk
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
