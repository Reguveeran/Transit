import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';

// Basemap Tile Providers (100% Free, Zero Key, No Watermark)
const TILE_LAYERS = {
  dark: {
    name: '🌙 Dark Canvas',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, HERE, Garmin, FAO, NOAA, USGS, &copy; OpenStreetMap contributors',
    maxZoom: 16,
  },
  satellite: {
    name: '🛰️ Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics, CNES/Airbus DS, USDA FSA, USGS, Aerogrid, IGN, IGP',
    maxZoom: 19,
  },
  osm: {
    name: '🗺️ OpenStreetMap',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  },
};

// Create custom DOM marker for vehicles by mode
const createVehicleIcon = (mode, status, isSelected) => {
  const normMode = (mode || 'bus').toLowerCase();
  const modeClass = `marker-${normMode}`;
  const selectedBorder = isSelected ? 'border: 3px solid #facc15; transform: scale(1.25); box-shadow: 0 0 15px rgba(250, 204, 21, 0.8);' : '';
  const symbol = (normMode === 'aircraft') ? '✈' : (normMode === 'ferry') ? '🚢' : (normMode === 'metro') ? 'M' : 'B';

  const iconHtml = `
    <div class="custom-vehicle-marker ${modeClass}" style="${selectedBorder}">
      <span>${symbol}</span>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'vehicle-div-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

// Create custom marker for Journey Start/End/Transfer points
const createJourneyPointIcon = (type, label) => {
  let bgColor = '#10b981'; // Origin
  let shadow = 'rgba(16, 185, 129, 0.7)';
  if (type === 'destination') {
    bgColor = '#ef4444'; // Destination
    shadow = 'rgba(239, 68, 68, 0.7)';
  } else if (type === 'transfer') {
    bgColor = '#8b5cf6'; // Transfer
    shadow = 'rgba(139, 92, 246, 0.7)';
  }

  const iconHtml = `
    <div style="
      background: ${bgColor};
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 2.5px solid white;
      box-shadow: 0 0 14px ${shadow}, 0 3px 8px rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 14px;
      font-family: system-ui, -apple-system, sans-serif;
    ">
      <span>${label}</span>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'journey-point-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

// Auto-adjust Leaflet camera viewport to fit route bounds
function MapBoundsUpdater({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length === 2 && bounds[0] && bounds[1]) {
      try {
        map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15 });
      } catch (err) {
        console.warn('Could not fit map bounds:', err);
      }
    }
  }, [bounds, map]);
  return null;
}

export default function LiveMap({
  vehicles,
  routes,
  stops,
  selectedVehicle,
  onSelectVehicle,
  activeJourney,
  onClearJourney,
}) {
  const defaultCenter = [12.9900, 80.2400];
  const [activeBaseLayer, setActiveBaseLayer] = useState('dark');
  const [filterMode, setFilterMode] = useState('all');

  const filteredVehicles = vehicles.filter((v) => {
    if (filterMode === 'all') return true;
    const vMode = (v.mode_name || v.mode || '').toLowerCase();
    return vMode === filterMode;
  });

  return (
    <div className="map-viewport" style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Journey Active Banner */}
      {activeJourney && (
        <div style={{
          position: 'absolute',
          top: 14,
          left: 64,
          zIndex: 1000,
          background: 'rgba(15, 23, 42, 0.92)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(59, 130, 246, 0.4)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
          borderRadius: '12px',
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: 'white',
          fontSize: '13px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: '#10b981', fontWeight: 700 }}>A</span>
            <span style={{ maxWidth: '130px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {activeJourney.origin}
            </span>
            <span style={{ color: '#94a3b8' }}>→</span>
            <span style={{ color: '#ef4444', fontWeight: 700 }}>B</span>
            <span style={{ maxWidth: '130px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {activeJourney.destination}
            </span>
          </div>
          <div style={{ width: '1px', height: '16px', background: 'rgba(255,255,255,0.2)' }} />
          <span style={{ color: '#60a5fa', fontWeight: 600 }}>
            {activeJourney.total_duration_minutes} min (ETA {activeJourney.estimated_arrival})
          </span>
          {onClearJourney && (
            <button
              onClick={onClearJourney}
              style={{
                background: 'rgba(239, 68, 68, 0.2)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                color: '#f87171',
                borderRadius: '6px',
                padding: '3px 8px',
                fontSize: '11px',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              Clear Route
            </button>
          )}
        </div>
      )}

      {/* 1. Basemap Style & Filter Overlay Controls */}
      <div style={{
        position: 'absolute',
        top: 14,
        right: 14,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        alignItems: 'flex-end',
      }}>
        {/* Layer Switcher */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          padding: '4px',
          display: 'flex',
          gap: '4px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)',
        }}>
          {Object.entries(TILE_LAYERS).map(([key, layer]) => (
            <button
              key={key}
              onClick={() => setActiveBaseLayer(key)}
              style={{
                background: activeBaseLayer === key ? '#3b82f6' : 'transparent',
                color: activeBaseLayer === key ? '#ffffff' : '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 10px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              {layer.name}
            </button>
          ))}
        </div>

        {/* Modality Filter */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          padding: '4px',
          display: 'flex',
          gap: '4px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)',
        }}>
          {[
            { id: 'all', label: 'All Modes' },
            { id: 'bus', label: '🚌 Buses' },
            { id: 'metro', label: '🚇 Metro' },
            { id: 'ferry', label: '🚢 Ships' },
            { id: 'aircraft', label: '✈️ Aircraft' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setFilterMode(item.id)}
              style={{
                background: filterMode === item.id ? '#10b981' : 'transparent',
                color: filterMode === item.id ? '#ffffff' : '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                padding: '5px 8px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
      >
        {/* Dynamic bounds updater when journey changes */}
        <MapBoundsUpdater bounds={activeJourney?.bounds} />

        {/* Crystal Clear, Zero-Watermark Tile Layer */}
        <TileLayer
          key={activeBaseLayer}
          attribution={TILE_LAYERS[activeBaseLayer].attribution}
          url={TILE_LAYERS[activeBaseLayer].url}
          maxZoom={TILE_LAYERS[activeBaseLayer].maxZoom}
        />

        {/* ========================================== */}
        {/* 0. ACTIVE JOURNEY OVERLAY PATHS & MARKERS */}
        {/* ========================================== */}
        {activeJourney && (
          <>
            {/* Polylines for each journey leg */}
            {activeJourney.recommended_journey?.map((leg, idx) => {
              const coords = leg.coordinates;
              if (!coords || coords.length < 2) return null;
              const isWalk = leg.type === 'WALK';
              const isTransfer = leg.type === 'TRANSFER';
              const legColor = isWalk ? '#10b981' : isTransfer ? '#a855f7' : (leg.color || '#3b82f6');

              return (
                <React.Fragment key={`journey-leg-${idx}`}>
                  {/* Glowing backlight */}
                  <Polyline
                    positions={coords}
                    pathOptions={{
                      color: legColor,
                      weight: isWalk || isTransfer ? 7 : 10,
                      opacity: 0.35,
                      dashArray: isWalk ? '8, 8' : isTransfer ? '6, 6' : undefined,
                    }}
                  />
                  {/* Sharp core polyline */}
                  <Polyline
                    positions={coords}
                    pathOptions={{
                      color: legColor,
                      weight: isWalk || isTransfer ? 3 : 5,
                      opacity: 0.95,
                      dashArray: isWalk ? '6, 8' : isTransfer ? '5, 5' : undefined,
                    }}
                  >
                    <Popup>
                      <div style={{ color: '#111827', padding: '4px' }}>
                        <strong style={{ fontSize: '13px' }}>{leg.type}: {leg.instruction || leg.line}</strong>
                        <p style={{ margin: '4px 0 0', fontSize: '12px' }}>
                          {leg.duration_minutes} min {leg.distance_km ? `(${leg.distance_km} km)` : leg.distance_meters ? `(${leg.distance_meters}m)` : ''}
                        </p>
                      </div>
                    </Popup>
                  </Polyline>
                </React.Fragment>
              );
            })}

            {/* Origin Point A Marker */}
            {activeJourney.origin_coord && (
              <Marker
                position={activeJourney.origin_coord}
                icon={createJourneyPointIcon('origin', 'A')}
              >
                <Popup>
                  <div style={{ color: '#111827', padding: '4px' }}>
                    <strong style={{ color: '#10b981', fontSize: '13px' }}>📍 Origin: {activeJourney.origin}</strong>
                    <p style={{ margin: '4px 0 0', fontSize: '12px' }}>
                      Departing at <strong>{activeJourney.departure_time || 'Now'}</strong>
                    </p>
                    <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#64748b' }}>
                      Boarding Stop: {activeJourney.origin_stop}
                    </p>
                  </div>
                </Popup>
              </Marker>
            )}

            {/* Destination Point B Marker */}
            {activeJourney.destination_coord && (
              <Marker
                position={activeJourney.destination_coord}
                icon={createJourneyPointIcon('destination', 'B')}
              >
                <Popup>
                  <div style={{ color: '#111827', padding: '4px' }}>
                    <strong style={{ color: '#ef4444', fontSize: '13px' }}>🏁 Destination: {activeJourney.destination}</strong>
                    <p style={{ margin: '4px 0 0', fontSize: '12px' }}>
                      ETA: <strong>{activeJourney.estimated_arrival}</strong> ({activeJourney.total_duration_minutes} min journey)
                    </p>
                    <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#64748b' }}>
                      Arrival Stop: {activeJourney.destination_stop}
                    </p>
                  </div>
                </Popup>
              </Marker>
            )}
          </>
        )}

        {/* 1. Route Polylines */}
        {routes.map((route) => {
          const coords = route.polyline_geojson?.coordinates;
          if (!coords || !coords.length) return null;
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
        {filteredVehicles.map((v) => {
          const lat = v.current_latitude;
          const lon = v.current_longitude;
          if (lat === null || lon === null || isNaN(lat) || isNaN(lon)) return null;

          const isSelected = selectedVehicle?.vehicle_id === v.vehicle_id;
          const modeStr = (v.mode_name || v.mode || 'bus').toLowerCase();

          return (
            <Marker
              key={v.vehicle_id}
              position={[lat, lon]}
              icon={createVehicleIcon(modeStr, v.status, isSelected)}
              eventHandlers={{
                click: () => onSelectVehicle(v),
              }}
            >
              <Popup>
                <div style={{ color: '#111827', minWidth: '170px', padding: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: '14px' }}>{v.label || v.vehicle_id}</strong>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: '#3b82f6' }}>
                      {modeStr.toUpperCase()}
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
