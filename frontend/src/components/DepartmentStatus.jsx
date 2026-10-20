import React, { useState, useEffect } from 'react';
import { Building, ShieldAlert, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import api from '../services/api';

export default function DepartmentStatus({ onSelectDepartment }) {
  const [departments, setDepartments] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDeptData() {
      try {
        const [depts, list] = await Promise.all([
          api.getDepartments(),
          api.getComplaints(),
        ]);
        setDepartments(depts);
        setComplaints(list);
      } catch (err) {
        console.error('Failed to load department status', err);
      } finally {
        setLoading(false);
      }
    }
    loadDeptData();
  }, []);

  if (loading) {
    return <div className="card"><p>Loading department workloads...</p></div>;
  }

  // Aggregate statistics per department from SQLite data
  const deptStats = departments.map((d) => {
    const deptComplaints = complaints.filter(c => c.department === d.name);
    return {
      name: d.name,
      id: d.department_id,
      authority: d.escalation_authority,
      total: deptComplaints.length,
      critical: deptComplaints.filter(c => c.priority === 'CRITICAL').length,
      high: deptComplaints.filter(c => c.priority === 'HIGH').length,
      in_progress: deptComplaints.filter(c => ['Assigned', 'In Progress'].includes(c.status)).length,
      resolved: deptComplaints.filter(c => ['Resolved', 'Closed'].includes(c.status)).length,
    };
  });

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <Building size={20} color="#1e3a8a" />
            Municipal Department Operational Queues
          </h2>
          <p className="card-subtitle">
            Department-oriented workload analysis calculated directly from database records.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {deptStats.map((ds) => (
          <div
            key={ds.id}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '1.25rem',
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1e3a8a' }}>
                  {ds.name}
                </h3>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  Authority: {ds.authority}
                </span>
              </div>
              <span className="badge badge-primary" style={{ fontSize: '0.9rem', padding: '0.3rem 0.6rem' }}>
                {ds.total} Assigned
              </span>
            </div>

            {/* Metrics Breakdown Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.6rem', marginTop: '0.85rem' }}>
              <div style={{ background: '#fef2f2', padding: '0.6rem', borderRadius: '6px', border: '1px solid #fecaca' }}>
                <span style={{ fontSize: '0.72rem', color: '#991b1b', fontWeight: 700, textTransform: 'uppercase' }}>
                  Critical (Immediate)
                </span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#b91c1c' }}>
                  {ds.critical}
                </div>
              </div>

              <div style={{ background: '#fff7ed', padding: '0.6rem', borderRadius: '6px', border: '1px solid #fed7aa' }}>
                <span style={{ fontSize: '0.72rem', color: '#c2410c', fontWeight: 700, textTransform: 'uppercase' }}>
                  High Priority
                </span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#c2410c' }}>
                  {ds.high}
                </div>
              </div>

              <div style={{ background: '#f0fdfa', padding: '0.6rem', borderRadius: '6px', border: '1px solid #ccfbf1' }}>
                <span style={{ fontSize: '0.72rem', color: '#0f766e', fontWeight: 700, textTransform: 'uppercase' }}>
                  In Progress
                </span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f766e' }}>
                  {ds.in_progress}
                </div>
              </div>

              <div style={{ background: '#f0fdf4', padding: '0.6rem', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                <span style={{ fontSize: '0.72rem', color: '#166534', fontWeight: 700, textTransform: 'uppercase' }}>
                  Resolved / Closed
                </span>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#166534' }}>
                  {ds.resolved}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
