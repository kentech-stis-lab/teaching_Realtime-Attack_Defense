import React from 'react';

export default function Layout({ wsConnected, attackPanel, defensePanel, monitorPanel, packetFilter, terminal }) {
  return (
    <>
      <header className="header">
        <div className="header-title">
          <span className="red">RED</span>
          <span className="sep">/</span>
          <span className="blue">BLUE</span>
          <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>Team Dashboard</span>
        </div>
        <div className="header-status">
          <span>
            <span
              className={`status-dot ${wsConnected ? 'healthy' : 'unhealthy'}`}
            />
            WebSocket {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <div className="main-grid">
        {/* Left: Attack Panel */}
        <div className="panel">
          <div className="panel-header red">
            <h2>Attack PoCs</h2>
          </div>
          <div className="panel-body">{attackPanel}</div>
        </div>

        {/* Center: Defense Panel */}
        <div className="panel">
          <div className="panel-header blue">
            <h2>IDS Rules</h2>
          </div>
          <div className="panel-body">{defensePanel}</div>
        </div>

        {/* Right: Monitor Panel */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="panel-header monitor">
            <h2>Live Monitor</h2>
          </div>
          {monitorPanel}
        </div>
      </div>

      {packetFilter}
      {terminal}
    </>
  );
}
