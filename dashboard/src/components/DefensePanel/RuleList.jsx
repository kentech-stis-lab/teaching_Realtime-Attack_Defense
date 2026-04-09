import React, { useState, useEffect, useCallback } from 'react';
import { fetchRules, toggleRule, deleteRule, reloadRules } from '../../api';
import RuleCard from './RuleCard';
import RuleEditor from './RuleEditor';
import CodeModal from '../common/CodeModal';

export default function RuleList({ appendTerminal }) {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [codeModal, setCodeModal] = useState(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchRules();
      setRules(Array.isArray(data) ? data : data.rules || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleToggle = async (rule) => {
    try {
      await toggleRule(rule.id);
      setRules((prev) =>
        prev.map((r) => r.id === rule.id ? { ...r, enabled: !r.enabled } : r)
      );
      appendTerminal(`[rule] ${rule.name} ${rule.enabled ? 'disabled' : 'enabled'}.`, 'info');
    } catch (e) {
      appendTerminal(`[error] ${e.message}`, 'stderr');
    }
  };

  const handleDelete = async (rule) => {
    if (!confirm(`Delete rule "${rule.name}"?`)) return;
    try {
      await deleteRule(rule.id);
      appendTerminal(`[rule] "${rule.name}" deleted.`, 'info');
      load();
    } catch (e) {
      appendTerminal(`[error] ${e.message}`, 'stderr');
    }
  };

  const handleReload = async () => {
    try {
      await reloadRules();
      appendTerminal('[rule] Suricata rules reloaded.', 'success');
      load();
    } catch (e) {
      appendTerminal(`[error] ${e.message}`, 'stderr');
    }
  };

  const handleSaved = () => {
    setShowEditor(false);
    load();
  };

  const presets = rules.filter((r) => r.is_preset !== false && !r.custom);
  const customs = rules.filter((r) => r.is_preset === false || r.custom);

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading rules...</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <p>Failed to load rules</p>
        <p style={{ fontSize: 10, marginTop: 4 }}>{error}</p>
        <button className="btn" style={{ marginTop: 8 }} onClick={load}>Retry</button>
      </div>
    );
  }

  return (
    <>
      <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
        <button className="btn btn-blue" onClick={() => setShowEditor(true)}>
          + New Rule
        </button>
        <button className="btn btn-green" onClick={handleReload}>
          Reload Rules
        </button>
      </div>

      {presets.length > 0 && (
        <>
          <div className="section-label">Preset</div>
          {presets.map((r) => (
            <RuleCard
              key={r.id}
              rule={r}
              onToggle={() => handleToggle(r)}
              onViewFull={() => setCodeModal({ title: r.name, code: r.content, language: 'text' })}
            />
          ))}
        </>
      )}

      {customs.length > 0 && (
        <>
          <div className="section-label">Custom</div>
          {customs.map((r) => (
            <RuleCard
              key={r.id}
              rule={r}
              isCustom
              onToggle={() => handleToggle(r)}
              onViewFull={() => setCodeModal({ title: r.name, code: r.content, language: 'text' })}
              onDelete={() => handleDelete(r)}
            />
          ))}
        </>
      )}

      {rules.length === 0 && (
        <div className="empty-state">No rules configured. Add one above.</div>
      )}

      {showEditor && (
        <RuleEditor onClose={() => setShowEditor(false)} onSaved={handleSaved} />
      )}

      {codeModal && (
        <CodeModal
          title={codeModal.title}
          code={codeModal.code}
          language={codeModal.language}
          onClose={() => setCodeModal(null)}
        />
      )}
    </>
  );
}
