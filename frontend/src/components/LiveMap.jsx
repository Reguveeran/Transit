import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import L from 'leaflet';

// Create custom DOM marker for vehicle
const createVehicleIcon = (mode, status, isSelected) => {
  const modeClass = `marker-${mode || 'bus'}`;
  const selectedBorder = isSelected ? 'border: 3px solid #facc15; transform: scale(1.2);' : '';
  const iconHtml = `
    <div class="custom-vehicle-marker ${modeClass}" style="${selectedBorder}">
      <span>${(mode || 'B')[0].toUpperCase()}</span>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'vehicle-div-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

export default function LiveMap({ vehicles, routes, stops, selectedVehicle, onSelectVehicle }) {
  const defaultCenter = [12.9900, 80.2400];

  return (
    <div className="map-viewport">
      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* 1. Route Polylines */}
        {routes.map((route) => {
          const coords = route.polyline_geojson?.coordinates;
          if (!coords || !coords.length) return null;
          // GeoJSON is [lon, lat], Leaflet wants [lat, lon]
          const latLngs = coords.map((c) => [c[1], c[0]]);
          return (
            <Polyline
              key={route.route_id}
              positions={latLngs}
              pathOptions={{
                color: route.color || '#3b82f6',
                weight: 4,
                opacity: 0.8,
              }}
            />
          );
        })}

        {/* 2. Transit Stops */}
        {stops.map((stop) => (
          <CircleMarker
            key={stop.stop_id}
            center={[stop.latitude, stop.longitude]}
            radius={5}
            pathOptions={{
              fillColor: '#ffffff',
              color: '#3b82f6',
              weight: 2,
              fillOpacity: 0.9,
            }}
          >
            <Popup>
              <div style={{ color: '#111827', padding: '4px' }}>
                <strong style={{ fontSize: '13px' }}>{stop.name}</strong>
                <p style={{ margin: '4px 0 0', fontSize: '11px', color: '#6b7280' }}>
                  Stop ID: {stop.stop_id} ({stop.code || 'Transit Station'})
                </p>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* 3. Live Vehicle Markers */}
        {vehicles.map((v) => {
          const lat = v.current_latitude;
          const lon = v.current_longitude;
          if (lat === null || lon === null || isNaN(lat) || isNaN(lon)) return null;

          const isSelected = selectedVehicle?.vehicle_id === v.vehicle_id;

          return (
            <Marker
              key={v.vehicle_id}
              position={[lat, lon]}
              icon={createVehicleIcon(v.mode_name || v.mode, v.status, isSelected)}
              eventHandlers={{
                click: () => onSelectVehicle(v),
              }}
            >
              <Popup>
                <div style={{ color: '#111827', minWidth: '160px', padding: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: '14px' }}>{v.vehicle_id}</strong>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: '#3b82f6' }}>
                      {v.mode_name?.toUpperCase()}
                    </span>
                  </div>
                  <p style={{ margin: '6px 0 2px', fontSize: '12px' }}>
                    Speed: <strong>{v.current_speed} km/h</strong>
                  </p>
                  <p style={{ margin: '2px 0', fontSize: '12px' }}>
                    Status: <span style={{ textTransform: 'capitalize' }}>{v.status?.toLowerCase()}</span>
                  </p>
                  {v.delay_seconds !== undefined && (
                    <p style={{ margin: '2px 0', fontSize: '12px', color: v.delay_seconds > 60 ? '#ef4444' : '#10b981' }}>
                      Delay: {v.delay_seconds > 0 ? `+${v.delay_seconds}s` : 'On Time'}
                    </p>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
