import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
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

export default function LiveMap({ vehicles, routes, stops, selectedVehicle, onSelectVehicle }) {
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
        {/* Crystal Clear, Zero-Watermark Tile Layer */}
        <TileLayer
          key={activeBaseLayer}
          attribution={TILE_LAYERS[activeBaseLayer].attribution}
          url={TILE_LAYERS[activeBaseLayer].url}
          maxZoom={TILE_LAYERS[activeBaseLayer].maxZoom}
        />

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
