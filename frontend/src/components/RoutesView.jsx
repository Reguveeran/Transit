import React from 'react';

export default function RoutesView({ routes }) {
  return (
    <div>
      <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
        Transit Lines & Routes
      </h3>

      {routes.map((route) => (
        <div key={route.route_id} className="transit-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <span
              style={{
                backgroundColor: route.color || '#3b82f6',
                color: route.text_color || '#ffffff',
                padding: '4px 8px',
                borderRadius: '6px',
                fontWeight: 800,
                fontSize: '12px',
              }}
            >
              {route.short_name}
            </span>
            <strong style={{ fontSize: '14px' }}>{route.long_name}</strong>
          </div>

          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Mode: <span style={{ textTransform: 'capitalize' }}>{route.mode_name}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
