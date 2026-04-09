import React, { useState, useEffect, useCallback } from 'react';
import { fetchAttacks, fetchAttack, runAttack, stopAttack, deleteAttack } from '../../api';
import AttackCard from './AttackCard';
import AttackEditor from './AttackEditor';
import CodeModal from '../common/CodeModal';

export default function AttackList({ appendTerminal, onAttackDone, onAttackStart }) {
  const [attacks, setAttacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [codeModal, setCodeModal] = useState(null);
  const [runningIds, setRunningIds] = useState(new Set());

  const load = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchAttacks();
      setAttacks(Array.isArray(data) ? data : data.attacks || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleRun = async (attack) => {
    try {
      setRunningIds((prev) => new Set(prev).add(attack.id));
      if (onAttackStart) onAttackStart(attack.id);
      appendTerminal(`[run] Starting "${attack.name}"...`, 'info');
      const result = await runAttack(attack.id);
      if (result.stdout) appendTerminal(result.stdout, 'stdout');
      if (result.stderr) appendTerminal(result.stderr, 'stderr');
      appendTerminal(`[run] "${attack.name}" completed.`, 'success');
      if (onAttackDone) onAttackDone();
    } catch (e) {
      appendTerminal(`[error] ${e.message}`, 'stderr');
    } finally {
      setRunningIds((prev) => {
        const next = new Set(prev);
        next.delete(attack.id);
        return next;
      });
    }
  };

  const handleStop = async (attack) => {
    try {
      await stopAttack(attack.id);
      appendTerminal(`[stop] "${attack.name}" stopped.`, 'info');
      setRunningIds((prev) => {
        const next = new Set(prev);
        next.delete(attack.id);
        return next;
      });
    } catch (e) {
      appendTerminal(`[error] ${e.message}`, 'stderr');
    }
  };

  const handleDelete = async (attack) => {
    if (!confirm(`Delete "${attack.name}"?`)) return;
    try {
      await deleteAttack(attack.id);
      appendTerminal(`[delete] "${attack.name}" removed.`, 'info');
      load();
    } catch (e) {
      appendTerminal(`[error] ${e.message}`, 'stderr');
    }
  };

  const handleSaved = () => {
    setShowEditor(false);
    setEditTarget(null);
    load();
  };

  const presets = attacks.filter((a) => a.is_preset !== false && !a.custom);
  const customs = attacks.filter((a) => a.is_preset === false || a.custom);

  if (loading) {
    return <div className="loading"><span className="spinner" />Loading attacks...</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <p>Failed to load attacks</p>
        <p style={{ fontSize: 10, marginTop: 4 }}>{error}</p>
        <button className="btn" style={{ marginTop: 8 }} onClick={load}>Retry</button>
      </div>
    );
  }

  return (
    <>
      <div style={{ marginBottom: 10 }}>
        <button className="btn btn-red" onClick={() => { setEditTarget(null); setShowEditor(true); }}>
          + New Attack
        </button>
      </div>

      {presets.length > 0 && (
        <>
          <div className="section-label">Preset</div>
          {presets.map((a) => (
            <AttackCard
              key={a.id}
              attack={a}
              isRunning={runningIds.has(a.id)}
              onRun={() => handleRun(a)}
              onStop={() => handleStop(a)}
              onViewCode={async () => { const detail = await fetchAttack(a.id); setCodeModal({ title: a.name, code: detail.code || '# No code available', language: a.language || 'python' }); }}
            />
          ))}
        </>
      )}

      {customs.length > 0 && (
        <>
          <div className="section-label">Custom</div>
          {customs.map((a) => (
            <AttackCard
              key={a.id}
              attack={a}
              isCustom
              isRunning={runningIds.has(a.id)}
              onRun={() => handleRun(a)}
              onStop={() => handleStop(a)}
              onViewCode={async () => { const detail = await fetchAttack(a.id); setCodeModal({ title: a.name, code: detail.code || '# No code available', language: a.language || 'python' }); }}
              onEdit={() => { setEditTarget(a); setShowEditor(true); }}
              onDelete={() => handleDelete(a)}
            />
          ))}
        </>
      )}

      {attacks.length === 0 && (
        <div className="empty-state">No attacks configured. Add one above.</div>
      )}

      {showEditor && (
        <AttackEditor
          attack={editTarget}
          onClose={() => { setShowEditor(false); setEditTarget(null); }}
          onSaved={handleSaved}
        />
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
