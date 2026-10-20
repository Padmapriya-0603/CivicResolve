import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Layers, CheckCircle } from 'lucide-react';
import api from '../services/api';

export default function Statistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getDashboard();
        setStats(data);
      } catch (err) {
        console.error('Failed to load stats', err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return <div className="card"><p>Loading statistical metrics...</p></div>;
  }

  const renderMeter = (label, count, total, color = '#1e3a8a') => {
    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
    return (
      <div key={label} style={{ marginBottom: '0.85rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
          <span style={{ fontWeight: 600, color: '#334155' }}>{label}</span>
          <span style={{ color: '#64748b' }}>{count} ({pct}%)</span>
        </div>
        <div style={{ width: '100%', height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '4px', transition: 'width 0.4s ease' }} />
        </div>
      </div>
    );
  };

  const total = stats?.total_complaints || 0;

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <BarChart3 size={20} color="#1e3a8a" />
              Empirical Grievance Statistics & Distribution
            </h2>
            <p className="card-subtitle">
              Auditable counts calculated by direct SQLite database aggregation. No simulated or randomized metrics.
            </p>
          </div>
          <span className="badge badge-primary">{total} Total Grievances</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {/* By Priority */}
          <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontWeight: 700, color: '#1e3a8a', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
              Breakdown by Priority Level
            </h4>
            {renderMeter('CRITICAL', stats.by_priority['CRITICAL'] || 0, total, '#b91c1c')}
            {renderMeter('HIGH', stats.by_priority['HIGH'] || 0, total, '#c2410c')}
            {renderMeter('MEDIUM', stats.by_priority['MEDIUM'] || 0, total, '#b45309')}
            {renderMeter('LOW', stats.by_priority['LOW'] || 0, total, '#15803d')}
          </div>

          {/* By Department */}
          <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontWeight: 700, color: '#1e3a8a', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
              Breakdown by Responsible Department
            </h4>
            {Object.entries(stats.by_department).map(([dept, cnt]) =>
              renderMeter(dept, cnt, total, '#1e3a8a')
            )}
          </div>

          {/* By Category */}
          <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontWeight: 700, color: '#1e3a8a', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
              Breakdown by Grievance Category
            </h4>
            {Object.entries(stats.by_category).map(([cat, cnt]) =>
              renderMeter(cat, cnt, total, '#0f766e')
            )}
          </div>

          {/* By Lifecycle Status */}
          <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontWeight: 700, color: '#1e3a8a', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.4rem' }}>
              Breakdown by Lifecycle Status
            </h4>
            {Object.entries(stats.by_status).map(([st, cnt]) =>
              renderMeter(st, cnt, total, '#475569')
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
