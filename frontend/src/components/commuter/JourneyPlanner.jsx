import React, { useState, useEffect } from 'react';
import { Navigation, Clock, ArrowRight, ShieldCheck, MapPin, Footprints, Bus, Train } from 'lucide-react';

const POPULAR_DESTINATIONS = [
  'SASTRA University / Tech Park',
  'Marina Coast Port & Pier',
  'Central Station Hub',
  'Airport Terminal Terminal 2',
  'Victoria Square North',
];

export default function JourneyPlanner({ onSelectJourney }) {
  const [origin, setOrigin] = useState('Current Location');
  const [destination, setDestination] = useState('SASTRA University / Tech Park');
  const [isLoading, setIsLoading] = useState(false);
  const [journey, setJourney] = useState(null);

  const fetchJourney = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/routes/plan_journey/?from=${encodeURIComponent(origin)}&to=${encodeURIComponent(destination)}`);
      const data = await res.json();
      setJourney(data);
    } catch (err) {
      console.error('Failed to plan journey:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJourney();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Origin & Destination Inputs */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}>
        <div>
          <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
            From
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
            <MapPin size={16} color="#10b981" />
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: 'white',
                fontSize: '13px',
              }}
            />
          </div>
        </div>

        <div>
          <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
            To
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
            <Navigation size={16} color="#3b82f6" />
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '8px 12px',
                color: 'white',
                fontSize: '13px',
              }}
            />
          </div>
        </div>

        {/* Quick Presets */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '4px' }}>
          {POPULAR_DESTINATIONS.map((dest) => (
            <button
              key={dest}
              onClick={() => { setDestination(dest); }}
              style={{
                background: destination === dest ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                border: destination === dest ? '1px solid #3b82f6' : '1px solid transparent',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '11px',
                color: destination === dest ? '#60a5fa' : '#94a3b8',
                cursor: 'pointer',
              }}
            >
              {dest.split('/')[0]}
            </button>
          ))}
        </div>

        <button
          onClick={fetchJourney}
          disabled={isLoading}
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            marginTop: '6px',
          }}
        >
          <Navigation size={16} />
          {isLoading ? 'Calculating Optimal Itinerary...' : 'Find Journey'}
        </button>
      </div>

      {/* Itinerary Result Card */}
      {journey && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
        }}>
          {/* Header Summary */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '11px', fontWeight: 600, color: '#10b981', textTransform: 'uppercase' }}>
                Recommended Route
              </span>
              <h3 style={{ margin: '2px 0 0', fontSize: '18px', fontWeight: 700 }}>
                {journey.total_duration_minutes} min
              </h3>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                Arrives by <strong>{journey.estimated_arrival}</strong>
              </div>
              <div style={{ fontSize: '11px', color: '#60a5fa' }}>
                {journey.transfers} Transfer • Saves {journey.co2_saved_kg}kg CO₂
              </div>
            </div>
          </div>

          {/* Timeline Steps */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '6px' }}>
            {journey.recommended_journey?.map((leg, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  gap: '12px',
                  alignItems: 'flex-start',
                  padding: '8px',
                  borderRadius: '8px',
                  background: leg.type === 'TRANSIT' ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
                  border: leg.type === 'TRANSIT' ? '1px solid rgba(59, 130, 246, 0.2)' : 'none',
                }}
              >
                <div style={{
                  fontSize: '18px',
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.05)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  {leg.icon}
                </div>
                <div style={{ flex: 1 }}>
                  {leg.type === 'TRANSIT' ? (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <strong style={{ fontSize: '13px', color: 'white' }}>
                          {leg.vehicle} — {leg.line}
                        </strong>
                        <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                          {leg.duration_minutes} min ({leg.distance_km} km)
                        </span>
                      </div>
                      <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                        {leg.departure_stop} → {leg.arrival_stop} ({leg.stops_count} stops)
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div style={{ fontSize: '13px', color: 'white' }}>
                        {leg.instruction}
                      </div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                        {leg.duration_minutes} min {leg.distance_meters ? `• ${leg.distance_meters}m` : ''}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
