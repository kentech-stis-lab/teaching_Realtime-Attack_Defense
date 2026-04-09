import React from 'react';

const CATEGORY_BADGE = {
  sqli: 'badge-sqli',
  xss: 'badge-xss',
  bruteforce: 'badge-bruteforce',
  bot: 'badge-bot',
  dos: 'badge-dos',
  portscan: 'badge-portscan',
  infiltration: 'badge-infiltration',
};

function getBadgeClass(category) {
  return CATEGORY_BADGE[category?.toLowerCase()] || 'badge-custom';
}

export default function AttackCard({
  attack,
  isCustom,
  isRunning,
  onRun,
  onStop,
  onViewCode,
  onEdit,
  onDelete,
}) {
  const status = isRunning ? 'running' : (attack.status || 'idle');

  return (
    <div className="card">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, minWidth: 0 }}>
          <span className={`status-dot ${status}`} />
          <span className="card-title" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {attack.name}
          </span>
        </div>
        <span className={`badge ${getBadgeClass(attack.category)}`}>
          {attack.category || 'custom'}
        </span>
      </div>

      {attack.cic_label && (
        <div className="card-meta">CIC-IDS: {attack.cic_label}</div>
      )}
      {attack.description && (
        <div className="card-meta">{attack.description}</div>
      )}

      <div className="card-footer">
        <div className="card-actions">
          <button className="btn btn-sm" onClick={onViewCode}>View Code</button>
          {!isRunning && (
            <button className="btn btn-sm btn-red" onClick={onRun}>&#9654; Run</button>
          )}
          {isRunning && (
            <button className="btn btn-sm btn-danger" onClick={onStop}>&#9632; Stop</button>
          )}
        </div>
        <div className="card-actions">
          {isCustom && onEdit && (
            <button className="btn btn-sm" onClick={onEdit}>Edit</button>
          )}
          {isCustom && onDelete && (
            <button className="btn btn-sm btn-danger" onClick={onDelete}>Del</button>
          )}
        </div>
      </div>
    </div>
  );
}
