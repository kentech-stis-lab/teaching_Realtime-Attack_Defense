import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { createAttack } from '../../api';

const CATEGORIES = ['SQLi', 'XSS', 'BruteForce', 'Bot', 'DoS', 'PortScan', 'Infiltration'];
const LANGUAGES = ['python', 'bash'];

export default function AttackEditor({ attack, onClose, onSaved }) {
  const [name, setName] = useState(attack?.name || '');
  const [category, setCategory] = useState(attack?.category || 'SQLi');
  const [language, setLanguage] = useState(attack?.language || 'python');
  const [description, setDescription] = useState(attack?.description || '');
  const [code, setCode] = useState(attack?.code || '# Write your attack PoC here\n');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    if (!name.trim()) { setError('Name is required'); return; }
    if (!code.trim()) { setError('Code is required'); return; }
    setSaving(true);
    setError(null);
    try {
      const id = name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '') || `custom_${Date.now()}`;
      const CIC_MAP = {
        SQLi: 'Web Attack - Sql Injection', XSS: 'Web Attack - XSS',
        BruteForce: 'Web Attack - Brute Force', Bot: 'Bot',
        DoS: 'DoS', PortScan: 'PortScan', Infiltration: 'Infiltration',
      };
      await createAttack({ id, name, category, language, description, code, cic_ids_label: CIC_MAP[category] || category });
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
          <h3>{attack ? 'Edit Attack' : 'New Attack PoC'}</h3>
          <button className="btn btn-sm" onClick={onClose}>X</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Name</label>
            <input className="form-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. SQL Injection - Login Bypass" />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label>Category</label>
              <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Language</label>
              <select className="form-select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea className="form-textarea" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Brief description..." rows={2} />
          </div>
          <div className="form-group">
            <label>Code</label>
            <div style={{ border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
              <Editor
                height="300px"
                language={language === 'bash' ? 'shell' : language}
                value={code}
                onChange={(val) => setCode(val || '')}
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
          <button className="btn btn-red" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
