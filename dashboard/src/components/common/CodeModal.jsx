import React from 'react';

export default function CodeModal({ title, code, language, onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 800 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title || 'Code'}</h3>
          <div style={{ display: 'flex', gap: 6 }}>
            <span style={{ fontSize: 10, color: 'var(--text-muted)', alignSelf: 'center' }}>{language}</span>
            <button className="btn btn-sm" onClick={onClose}>X</button>
          </div>
        </div>
        <div className="modal-body" style={{ padding: 0 }}>
          <pre style={{
            margin: 0,
            padding: '12px 16px',
            background: '#1e1e1e',
            color: '#d4d4d4',
            fontSize: 13,
            lineHeight: 1.5,
            fontFamily: "'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
            overflow: 'auto',
            maxHeight: 450,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}>
            <code>{code || '// No code available'}</code>
          </pre>
        </div>
        <div className="modal-footer">
          <button className="btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
