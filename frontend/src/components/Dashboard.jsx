import React, { useState, useEffect } from 'react';
import {
  FileText,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Building,
  Zap,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Send,
  Eye
} from 'lucide-react';
import api from '../services/api';

export default function Dashboard({ onNavigate, onSelectComplaint }) {
  const [stats, setStats] = useState(null);
  const [recentComplaints, setRecentComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [dashData, compList] = await Promise.all([
          api.getDashboard(),
          api.getComplaints(),
        ]);
        setStats(dashData);
        setRecentComplaints(compList.slice(0, 5));
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  if (loading) {
    return <div className="card"><p>Loading live civic dashboard metrics...</p></div>;
  }

  const getPriorityBadge = (p) => {
    switch (p?.toUpperCase()) {
      case 'CRITICAL': return <span className="badge badge-critical">CRITICAL</span>;
      case 'HIGH': return <span className="badge badge-high">HIGH</span>;
      case 'MEDIUM': return <span className="badge badge-medium">MEDIUM</span>;
      default: return <span className="badge badge-low">LOW</span>;
    }
  };

  return (
    <div>
      {/* Civic Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)', color: '#ffffff', border: 'none' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.85 }}>
              Deterministic Municipal Administration Engine
            </span>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.2rem' }}>
              Public Grievance Routing & Reasoning Dashboard
            </h1>
            <p style={{ fontSize: '0.9rem', opacity: 0.9, maxWidth: '750px', marginTop: '0.4rem' }}>
              Deterministic public service management utilizing Knowledge Representation, Constraint Satisfaction (CSP), and Forward Chaining Deduction. Guaranteed zero black-box LLM hallucinations.
            </p>
          </div>
          <button
            className="btn"
            style={{ backgroundColor: '#ffffff', color: '#1e3a8a', fontWeight: 700 }}
            onClick={() => onNavigate('submit')}
          >
            <Send size={16} />
            File New Grievance
          </button>
        </div>
      </div>

      {/* Top Level Metric KPIs */}
      <div className="stats-grid">
        <div className="stat-box primary">
          <span className="stat-label">Total Grievances</span>
          <div className="stat-value">{stats.total_complaints}</div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Recorded in SQLite database</span>
        </div>

        <div className="stat-box critical">
          <span className="stat-label">Critical Priority</span>
          <div className="stat-value" style={{ color: '#b91c1c' }}>{stats.critical_complaints}</div>
          <span style={{ fontSize: '0.75rem', color: '#b91c1c' }}>Immediate life/safety risk</span>
        </div>

        <div className="stat-box high">
          <span className="stat-label">High Priority</span>
          <div className="stat-value" style={{ color: '#c2410c' }}>{stats.high_priority_complaints}</div>
          <span style={{ fontSize: '0.75rem', color: '#c2410c' }}>Widespread public disruption</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #7c3aed' }}>
          <span className="stat-label">Escalated Grievances</span>
          <div className="stat-value" style={{ color: '#7c3aed' }}>{stats.escalated_complaints}</div>
          <span style={{ fontSize: '0.75rem', color: '#7c3aed' }}>Dispatched to Chief Engineers</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #0f766e' }}>
          <span className="stat-label">In-Progress Tasks</span>
          <div className="stat-value" style={{ color: '#0f766e' }}>{stats.in_progress_complaints}</div>
          <span style={{ fontSize: '0.75rem', color: '#0f766e' }}>Active field operations</span>
        </div>

        <div className="stat-box low">
          <span className="stat-label">Resolved / Closed</span>
          <div className="stat-value" style={{ color: '#15803d' }}>{stats.resolved_complaints}</div>
          <span style={{ fontSize: '0.75rem', color: '#15803d' }}>Successfully completed</span>
        </div>
      </div>

      {/* Distribution Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Department Load Breakdown */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Building size={18} color="#1e3a8a" />
              Grievance Load by Department
            </h3>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem' }} onClick={() => onNavigate('departments')}>
              View Queues &rarr;
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {Object.entries(stats.by_department).map(([dept, count]) => {
              const pct = stats.total_complaints > 0 ? Math.round((count / stats.total_complaints) * 100) : 0;
              return (
                <div key={dept}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.2rem' }}>
                    <span style={{ fontWeight: 600, color: '#334155' }}>{dept}</span>
                    <span style={{ color: '#64748b' }}>{count} ({pct}%)</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: '#e2e8f0', borderRadius: '3px' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: '#1e3a8a', borderRadius: '3px' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Priority Hierarchy & Status Summary */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Zap size={18} color="#d97706" />
              Priority Distribution & Resolution
            </h3>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem' }} onClick={() => onNavigate('statistics')}>
              Full Analytics &rarr;
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginTop: '0.5rem' }}>
            <div style={{ background: '#fef2f2', padding: '1rem', borderRadius: '8px', border: '1px solid #fecaca' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#991b1b' }}>CRITICAL HAZARDS</span>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#b91c1c' }}>
                {stats.by_priority['CRITICAL'] || 0}
              </div>
              <span style={{ fontSize: '0.75rem', color: '#991b1b' }}>Immediate Escalation Tier</span>
            </div>

            <div style={{ background: '#fff7ed', padding: '1rem', borderRadius: '8px', border: '1px solid #fed7aa' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#c2410c' }}>HIGH PRIORITY</span>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#c2410c' }}>
                {stats.by_priority['HIGH'] || 0}
              </div>
              <span style={{ fontSize: '0.75rem', color: '#c2410c' }}>High Population / Recurrent</span>
            </div>

            <div style={{ background: '#fefce8', padding: '1rem', borderRadius: '8px', border: '1px solid #fef08a' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#b45309' }}>MEDIUM PRIORITY</span>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#b45309' }}>
                {stats.by_priority['MEDIUM'] || 0}
              </div>
              <span style={{ fontSize: '0.75rem', color: '#b45309' }}>Noticeable Civic Disruption</span>
            </div>

            <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#166534' }}>LOW PRIORITY</span>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#166534' }}>
                {stats.by_priority['LOW'] || 0}
              </div>
              <span style={{ fontSize: '0.75rem', color: '#166534' }}>Standard Scheduled Queue</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Grievances Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Clock size={18} />
              Recent Processed Grievances
            </h3>
            <p className="card-subtitle">
              Live incoming citizen submissions routed by the forward chaining engine.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={() => onNavigate('history')}>
            View All ({stats.total_complaints}) &rarr;
          </button>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Complaint ID</th>
                <th>Citizen Name</th>
                <th>Category</th>
                <th>Issue Type</th>
                <th>Department</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentComplaints.map((c) => (
                <tr key={c.complaint_id}>
                  <td><strong>{c.complaint_id}</strong></td>
                  <td>{c.citizen_name}</td>
                  <td>{c.category}</td>
                  <td>{c.issue_type}</td>
                  <td><span style={{ fontWeight: 600, color: '#1e3a8a' }}>{c.department}</span></td>
                  <td>{getPriorityBadge(c.priority)}</td>
                  <td><span className="badge badge-neutral">{c.status}</span></td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem' }}
                      onClick={() => onSelectComplaint(c.complaint_id)}
                    >
                      <Eye size={14} />
                      Inspect Trace
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
