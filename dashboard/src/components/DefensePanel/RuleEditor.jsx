import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { createRule } from '../../api';

const CATEGORIES = ['SQLi', 'XSS', 'BruteForce', 'Bot', 'DoS', 'PortScan', 'Infiltration', 'General'];

const TEMPLATE = `alert http any any -> any any (msg:"Custom Rule"; flow:to_server,established; content:"pattern"; sid:9000001; rev:1;)`;

export default function RuleEditor({ onClose, onSaved }) {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('General');
  const [content, setContent] = useState(TEMPLATE);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    if (!name.trim()) { setError('Name is required'); return; }
    if (!content.trim()) { setError('Rule content is required'); return; }
    setSaving(true);
    setError(null);
    try {
      await createRule({ name, category, content });
      onSaved();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>New Suricata Rule</h3>
          <button className="btn btn-sm" onClick={onClose}>X</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Name</label>
            <input className="form-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Detect SQL Injection in Login" />
          </div>
          <div className="form-group">
            <label>Category</label>
            <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Suricata Rule</label>
            <div style={{ border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
              <Editor
                height="250px"
                language="text"
                value={content}
                onChange={(val) => setContent(val || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  padding: { top: 8 },
                }}
              />
            </div>
          </div>
          {error && <div style={{ color: 'var(--severity-high)', fontSize: 12 }}>{error}</div>}
        </div>
        <div className="modal-footer">
          <button className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-blue" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save & Apply'}
          </button>
        </div>
      </div>
    </div>
  );
}
