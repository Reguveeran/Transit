import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket() {
  const [vehicleUpdates, setVehicleUpdates] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connecting');

  const vehicleWsRef = useRef(null);
  const alertWsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);

  const connectWebSockets = useCallback(() => {
    // Clear any existing reconnect timer
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsBase = `${protocol}//${host}/ws`;

    setConnectionStatus(retryCountRef.current === 0 ? 'connecting' : 'reconnecting');

    // 1. Vehicle Telemetry WebSocket
    try {
      const vWs = new WebSocket(`${wsBase}/vehicles/`);
      vehicleWsRef.current = vWs;

      vWs.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        retryCountRef.current = 0;
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
        setConnectionStatus('disconnected');

        // Exponential backoff: 1s, 1.5s, 2.25s ... capped at 15s
        const backoffMs = Math.min(15000, 1000 * Math.pow(1.5, retryCountRef.current));
        retryCountRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(connectWebSockets, backoffMs);
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
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (vehicleWsRef.current) vehicleWsRef.current.close();
      if (alertWsRef.current) alertWsRef.current.close();
    };
  }, [connectWebSockets]);

  return { vehicleUpdates, alerts, isConnected, connectionStatus };
}
