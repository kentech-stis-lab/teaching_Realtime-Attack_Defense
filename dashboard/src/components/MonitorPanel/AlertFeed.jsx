import React, { useEffect, useRef } from 'react';

function formatTime(ts) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return '--:--:--';
  }
}

function severityLabel(sev) {
  if (sev === 1) return 'HIGH';
  if (sev === 2) return 'MED';
  return 'LOW';
}

export default function AlertFeed({ alerts, onClear }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [alerts.length]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          {alerts.length} alert{alerts.length !== 1 ? 's' : ''}
        </span>
        {alerts.length > 0 && (
          <button className="btn btn-sm" onClick={onClear}>Clear</button>
        )}
      </div>

      {alerts.length === 0 ? (
        <div className="empty-state">Waiting for alerts...</div>
      ) : (
        <div>
          {alerts.map((alert) => (
            <div className="alert-item" key={alert.id}>
              <span className="alert-time">{formatTime(alert.timestamp)}</span>
              <span className={`severity-badge severity-${alert.severity}`}>
                {severityLabel(alert.severity)}
              </span>
              <span className="alert-msg">{alert.message}</span>
              <span className="alert-src">{alert.src_ip}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
