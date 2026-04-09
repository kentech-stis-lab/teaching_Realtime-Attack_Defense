const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

// ===== Attacks =====
export function fetchAttacks() {
  return request('/attacks');
}

export function fetchAttack(id) {
  return request(`/attacks/${id}`);
}

export function runAttack(id) {
  return request(`/attacks/${id}/run`, { method: 'POST' });
}

export function stopAttack(id) {
  return request(`/attacks/${id}/stop`, { method: 'POST' });
}

export function createAttack(data) {
  return request('/attacks', { method: 'POST', body: JSON.stringify(data) });
}

export function deleteAttack(id) {
  return request(`/attacks/${id}`, { method: 'DELETE' });
}

// ===== Rules =====
export async function fetchRules() {
  const data = await request('/rules');
  return data.map((r) => ({
    id: r.sid || r.id,
    sid: r.sid,
    name: r.msg || r.name || `SID ${r.sid}`,
    content: r.raw || r.content || '',
    enabled: r.enabled !== false,
    is_preset: r.source_file === 'preset',
    source_file: r.source_file,
  }));
}

export function toggleRule(id) {
  return request(`/rules/${id}/toggle`, { method: 'PUT' });
}

export function createRule(data) {
  return request('/rules', { method: 'POST', body: JSON.stringify(data) });
}

export function deleteRule(id) {
  return request(`/rules/${id}`, { method: 'DELETE' });
}

export function reloadRules() {
  return request('/rules/reload', { method: 'POST' });
}

// ===== Alerts =====
export function fetchAlerts() {
  return request('/alerts');
}

export function fetchAlertStats() {
  return request('/alerts/stats');
}

export function clearAlertsApi() {
  return request('/alerts', { method: 'DELETE' });
}

// ===== Status =====
export function fetchStatus() {
  return request('/status');
}
