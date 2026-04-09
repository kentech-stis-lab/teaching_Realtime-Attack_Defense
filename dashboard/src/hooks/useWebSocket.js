import { useState, useEffect, useRef, useCallback } from 'react';

const MAX_ALERTS = 200;
const RECONNECT_DELAY = 3000;

export default function useWebSocket() {
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/alerts`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (mountedRef.current) {
          setConnected(true);
        }
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ping') return; // ignore keepalive
          const alert = {
            id: data.id || Date.now() + Math.random(),
            timestamp: data.timestamp || new Date().toISOString(),
            src_ip: data.src_ip || data.source_ip || 'unknown',
            dest_ip: data.dest_ip || data.dest_ip || '',
            message: data.signature || data.message || data.msg || data.alert?.signature || 'Unknown alert',
            severity: data.severity || data.alert?.severity || 3,
            category: data.category || data.alert?.category || 'unknown',
            sid: data.signature_id || data.sid || data.alert?.signature_id || 0,
          };
          setAlerts((prev) => {
            const updated = [...prev, alert];
            return updated.length > MAX_ALERTS ? updated.slice(-MAX_ALERTS) : updated;
          });
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        if (mountedRef.current) {
          setConnected(false);
          reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  const clearAlerts = useCallback(() => setAlerts([]), []);

  return { alerts, connected, clearAlerts };
}
