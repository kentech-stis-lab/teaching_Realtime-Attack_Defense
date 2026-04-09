import React from 'react';

export default function RuleCard({ rule, isCustom, onToggle, onViewFull, onDelete }) {
  const firstLine = rule.content
    ? rule.content.split('\n')[0].substring(0, 80)
    : '';

  return (
    <div className="card">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0 }}>
          <label className="toggle" onClick={(e) => e.stopPropagation()}>
            <input type="checkbox" checked={rule.enabled !== false} onChange={onToggle} />
            <span className="toggle-slider" />
          </label>
          <span className="card-title" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {rule.name}
          </span>
        </div>
        {rule.sid && (
          <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'monospace' }}>
            SID:{rule.sid}
          </span>
        )}
      </div>

      {firstLine && <div className="rule-preview">{firstLine}</div>}

      <div className="card-footer" style={{ marginTop: 6 }}>
        <button className="btn btn-sm" onClick={onViewFull}>View Full</button>
        <div className="card-actions">
          {isCustom && onDelete && (
            <button className="btn btn-sm btn-danger" onClick={onDelete}>Delete</button>
          )}
        </div>
      </div>
    </div>
  );
}
