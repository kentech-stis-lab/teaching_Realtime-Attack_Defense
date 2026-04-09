import React, { useState, useEffect } from 'react';
import { fetchStatus } from '../../api';

const DEFAULT_SERVICES = [
  { name: 'Backend API', key: 'backend' },
  { name: 'Suricata IDS', key: 'suricata' },
  { name: 'Attack Runner', key: 'attack_runner' },
  { name: 'Log Collector', key: 'log_collector' },
  { name: 'Database', key: 'database' },
  { name: 'Dashboard', key: 'dashboard' },
];

export default function SystemStatus() {
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const data = await fetchStatus();
        if (mounted) {
          setStatus(data.services || data);
          setError(null);
        }
      } catch (e) {
        if (mounted) setError(e.message);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();
    const interval = setInterval(load, 10000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  if (loading) {
    return <div className="loading"><span className="spinner" />Checking services...</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <p>Cannot reach backend</p>
        <p style={{ fontSize: 10, marginTop: 4 }}>{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="section-label">Services</div>
      <div className="status-grid">
        {DEFAULT_SERVICES.map((svc) => {
          const state = status[svc.key];
          const healthy = state === 'healthy' || state === 'running' || state === true;
          return (
            <div className="status-item" key={svc.key}>
              <span className={`status-dot ${healthy ? 'healthy' : 'unhealthy'}`} />
              <span>{svc.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
