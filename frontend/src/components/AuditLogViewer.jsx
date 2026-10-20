import React, { useState, useEffect } from 'react';
import { History, Shield, RefreshCw, Search } from 'lucide-react';
import api from '../services/api';

export default function AuditLogViewer() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs(300);
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = logs.filter(l =>
    !search ||
    l.action?.toLowerCase().includes(search.toLowerCase()) ||
    l.user_email?.toLowerCase().includes(search.toLowerCase()) ||
    l.entity_type?.toLowerCase().includes(search.toLowerCase()) ||
    l.entity_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <History size={20} color="#1e3a8a" />
            System Audit Trail & Security Logs
          </h2>
          <p className="card-subtitle">
            Immutable administrative records capturing logins, status shifts, department overrides, user management, and rule modifications.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadLogs} disabled={loading}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
        </button>
      </div>

      <div style={{ marginBottom: '1.25rem', maxWidth: '350px' }}>
        <input
          type="text"
          className="form-input"
          placeholder="Filter by action, email, entity..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp</th>
              <th>Action</th>
              <th>User / Actor</th>
              <th>Entity</th>
              <th>Old State</th>
              <th>New State</th>
              <th>Reason / Justification</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map((log) => (
              <tr key={log.id}>
                <td><strong>#{log.id}</strong></td>
                <td style={{ fontSize: '0.78rem', color: '#64748b' }}>
                  {log.timestamp}
                </td>
                <td>
                  <span className="badge badge-primary" style={{ fontSize: '0.72rem' }}>
                    {log.action}
                  </span>
                </td>
                <td>
                  <div style={{ fontWeight: 600 }}>{log.user_email || 'System'}</div>
                  {log.user_id && <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>ID: {log.user_id}</span>}
                </td>
                <td>
                  <span style={{ fontWeight: 500 }}>{log.entity_type}</span>
                  {log.entity_id && <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{log.entity_id}</div>}
                </td>
                <td style={{ fontSize: '0.78rem', color: '#64748b', maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {log.old_value || '—'}
                </td>
                <td style={{ fontSize: '0.78rem', color: '#0f766e', fontWeight: 600, maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {log.new_value || '—'}
                </td>
                <td style={{ fontSize: '0.8rem', color: '#334155' }}>
                  {log.reason || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
