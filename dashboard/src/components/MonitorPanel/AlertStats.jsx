import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const CATEGORY_COLORS = {
  sqli: '#d18616',
  xss: '#8957e5',
  bruteforce: '#f87171',
  bot: '#39c5cf',
  dos: '#c9a81c',
  portscan: '#4ade80',
  infiltration: '#db61a2',
  unknown: '#6e7681',
};

function getColor(cat) {
  return CATEGORY_COLORS[cat?.toLowerCase()] || CATEGORY_COLORS.unknown;
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border)',
      borderRadius: 4,
      padding: '6px 10px',
      fontSize: 12,
    }}>
      <div style={{ fontWeight: 600 }}>{d.category}</div>
      <div style={{ color: 'var(--text-secondary)' }}>{d.count} alerts</div>
    </div>
  );
};

export default function AlertStats({ alerts }) {
  const data = useMemo(() => {
    const counts = {};
    alerts.forEach((a) => {
      const cat = (a.category || 'unknown').toLowerCase();
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);
  }, [alerts]);

  const severityData = useMemo(() => {
    const counts = { 1: 0, 2: 0, 3: 0 };
    alerts.forEach((a) => {
      const sev = a.severity || 3;
      counts[sev] = (counts[sev] || 0) + 1;
    });
    return [
      { label: 'High', severity: 1, count: counts[1], color: '#f85149' },
      { label: 'Medium', severity: 2, count: counts[2], color: '#d29922' },
      { label: 'Low', severity: 3, count: counts[3], color: '#e3b341' },
    ];
  }, [alerts]);

  if (alerts.length === 0) {
    return <div className="empty-state">No alerts yet to chart.</div>;
  }

  return (
    <div>
      <div className="stats-container">
        <div className="stats-title">Alerts by Category</div>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={data} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
            <XAxis dataKey="category" tick={{ fontSize: 10, fill: '#8b949e' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#8b949e' }} axisLine={false} tickLine={false} width={30} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
            <Bar dataKey="count" radius={[3, 3, 0, 0]}>
              {data.map((entry, i) => (
                <Cell key={i} fill={getColor(entry.category)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="stats-container">
        <div className="stats-title">Alerts by Severity</div>
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={severityData} layout="vertical" margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
            <XAxis type="number" tick={{ fontSize: 10, fill: '#8b949e' }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="label" tick={{ fontSize: 11, fill: '#8b949e' }} axisLine={false} tickLine={false} width={50} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
            <Bar dataKey="count" radius={[0, 3, 3, 0]}>
              {severityData.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
        Total: {alerts.length} alerts
      </div>
    </div>
  );
}
