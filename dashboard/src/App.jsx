import React, { useState, useCallback, useEffect, useRef } from 'react';
import Layout from './components/Layout';
import AttackList from './components/AttackPanel/AttackList';
import RuleList from './components/DefensePanel/RuleList';
import AlertFeed from './components/MonitorPanel/AlertFeed';
import AlertStats from './components/MonitorPanel/AlertStats';
import SystemStatus from './components/MonitorPanel/SystemStatus';
import Terminal from './components/common/Terminal';
import PacketFilter from './components/common/PacketFilter';
import useWebSocket from './hooks/useWebSocket';
import { fetchAlerts, clearAlertsApi } from './api';

function mapAlert(a, i) {
  return {
    id: `alert-${a.signature_id || 0}-${a.timestamp}-${i}`,
    timestamp: a.timestamp,
    src_ip: a.src_ip || 'unknown',
    message: a.signature || a.message || 'Unknown',
    severity: a.severity || 3,
    category: a.category || 'unknown',
    sid: a.signature_id || 0,
  };
}

export default function App() {
  const [terminalLines, setTerminalLines] = useState([
    { text: '[dashboard] Ready. Click "Run" on an attack to start.', type: 'info' },
  ]);
  const [monitorTab, setMonitorTab] = useState('feed');
  const [activeAttackId, setActiveAttackId] = useState(null);
  const { alerts: wsAlerts, connected, clearAlerts } = useWebSocket();
  const [polledAlerts, setPolledAlerts] = useState([]);
  const lastAlertCount = useRef(0);

  // Load alerts and poll every 3 seconds
  const loadAlerts = useCallback(async () => {
    try {
      const data = await fetchAlerts();
      const mapped = data.map(mapAlert);
      setPolledAlerts(mapped);
    } catch {}
  }, []);

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 3000);
    return () => clearInterval(interval);
  }, [loadAlerts]);

  // Merge: use polled alerts as ground truth (deduplicated)
  const allAlerts = polledAlerts;

  const appendTerminal = useCallback((text, type = 'stdout') => {
    setTerminalLines((prev) => {
      const next = [...prev, { text, type, ts: Date.now() }];
      return next.length > 500 ? next.slice(-500) : next;
    });
  }, []);

  const clearTerminal = useCallback(() => {
    setTerminalLines([]);
  }, []);

  // Trigger alert reload after attack
  const onAttackDone = useCallback(() => {
    setTimeout(loadAlerts, 500);
  }, [loadAlerts]);

  return (
    <Layout
      wsConnected={connected}
      attackPanel={<AttackList appendTerminal={appendTerminal} onAttackDone={onAttackDone} onAttackStart={setActiveAttackId} />}
      defensePanel={<RuleList appendTerminal={appendTerminal} />}
      monitorPanel={
        <>
          <div className="monitor-tabs">
            <button
              className={`monitor-tab ${monitorTab === 'feed' ? 'active' : ''}`}
              onClick={() => setMonitorTab('feed')}
            >
              Live Feed
            </button>
            <button
              className={`monitor-tab ${monitorTab === 'stats' ? 'active' : ''}`}
              onClick={() => setMonitorTab('stats')}
            >
              Statistics
            </button>
            <button
              className={`monitor-tab ${monitorTab === 'status' ? 'active' : ''}`}
              onClick={() => setMonitorTab('status')}
            >
              System
            </button>
          </div>
          <div className="panel-body">
            {monitorTab === 'feed' && <AlertFeed alerts={allAlerts} onClear={() => { clearAlertsApi().catch(() => {}); setPolledAlerts([]); }} />}
            {monitorTab === 'stats' && <AlertStats alerts={allAlerts} />}
            {monitorTab === 'status' && <SystemStatus />}
          </div>
        </>
      }
      packetFilter={<PacketFilter activeAttackId={activeAttackId} />}
      terminal={
        <Terminal lines={terminalLines} onClear={clearTerminal} />
      }
    />
  );
}
