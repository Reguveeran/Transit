import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket() {
  const [vehicleUpdates, setVehicleUpdates] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const vehicleWsRef = useRef(null);
  const alertWsRef = useRef(null);

  const connectWebSockets = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsBase = `${protocol}//${host}/ws`;

    // 1. Vehicle Telemetry WebSocket
    try {
      const vWs = new WebSocket(`${wsBase}/vehicles/`);
      vehicleWsRef.current = vWs;

      vWs.onopen = () => {
        setIsConnected(true);
      };

      vWs.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.vehicle_id) {
            setVehicleUpdates((prev) => ({
              ...prev,
              [data.vehicle_id]: {
                ...data,
                receivedAt: Date.now(),
              },
            }));
          }
        } catch (err) {
          console.error('Error parsing vehicle WS message', err);
        }
      };

      vWs.onclose = () => {
        setIsConnected(false);
        setTimeout(connectWebSockets, 3000);
      };
    } catch (e) {
      console.warn('WS connection notice:', e);
    }

    // 2. Alerts WebSocket
    try {
      const aWs = new WebSocket(`${wsBase}/alerts/`);
      alertWsRef.current = aWs;

      aWs.onmessage = (event) => {
        try {
          const alertData = JSON.parse(event.data);
          if (alertData && alertData.message) {
            setAlerts((prev) => [alertData, ...prev.slice(0, 9)]);
          }
        } catch (err) {
          console.error('Error parsing alert WS message', err);
        }
      };
    } catch (e) {
      console.warn('Alerts WS connection notice:', e);
    }
  }, []);

  useEffect(() => {
    connectWebSockets();
    return () => {
      if (vehicleWsRef.current) vehicleWsRef.current.close();
      if (alertWsRef.current) alertWsRef.current.close();
    };
  }, [connectWebSockets]);

  return { vehicleUpdates, alerts, isConnected };
}
