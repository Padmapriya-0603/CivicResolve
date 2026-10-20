import React, { useState, useEffect } from 'react';
import { Search, Filter, Eye, RefreshCw, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function ComplaintHistory({ onSelectComplaint }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [categories, setCategories] = useState([]);

  // Filters
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [list, depts, cats] = await Promise.all([
        api.getComplaints({
          search,
          category: categoryFilter,
          department: deptFilter,
          priority: priorityFilter,
          status: statusFilter,
        }),
        api.getDepartments(),
        api.getCategories(),
      ]);
      setComplaints(list);
      setDepartments(depts);
      setCategories(cats);
    } catch (err) {
      console.error('Failed to load complaints', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [categoryFilter, deptFilter, priorityFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const getPriorityBadge = (p) => {
    switch (p?.toUpperCase()) {
      case 'CRITICAL': return <span className="badge badge-critical">CRITICAL</span>;
      case 'HIGH': return <span className="badge badge-high">HIGH</span>;
      case 'MEDIUM': return <span className="badge badge-medium">MEDIUM</span>;
      default: return <span className="badge badge-low">LOW</span>;
    }
  };

  const getEscalationBadge = (e) => {
    switch (e?.toUpperCase()) {
      case 'IMMEDIATE': return <span className="badge badge-critical">IMMEDIATE</span>;
      case 'REQUIRED': return <span className="badge badge-high">REQUIRED</span>;
      default: return <span className="badge badge-neutral">NONE</span>;
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            Municipal Grievance Registry & Audit Log
          </h2>
          <p className="card-subtitle">
            Historical database of all registered grievances, assigned departments, and status transitions.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Filter Controls Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.4rem' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search citizen, ID, loc..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary" style={{ padding: '0.5rem 0.75rem' }}>
            <Search size={16} />
          </button>
        </form>

        <select
          className="form-select"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.category_id} value={c.name}>{c.name}</option>
          ))}
        </select>

        <select
          className="form-select"
          value={deptFilter}
          onChange={(e) => setDeptFilter(e.target.value)}
        >
          <option value="">All Departments</option>
          {departments.map((d) => (
            <option key={d.department_id} value={d.name}>{d.name}</option>
          ))}
        </select>

        <select
          className="form-select"
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
        >
          <option value="">All Priorities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>

        <select
          className="form-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="SUBMITTED">1. Submitted</option>
          <option value="ACKNOWLEDGED">2. Acknowledged</option>
          <option value="IN_PROGRESS">3. In Progress</option>
          <option value="RESOLVED">4. Resolved</option>
          <option value="CLOSED">5. Closed</option>
        </select>
      </div>

      {/* Grievance Table */}
      {complaints.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
          No grievances found matching the selected criteria.
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Complaint ID</th>
                <th>Date</th>
                <th>Category</th>
                <th>Issue Type</th>
                <th>Location / Ward</th>
                <th>Department</th>
                <th>Priority</th>
                <th>Escalation</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((c) => (
                <tr key={c.complaint_id}>
                  <td>
                    <strong>{c.complaint_id}</strong>
                    {c.evidence_filename && (
                      <div style={{ marginTop: '0.2rem' }}>
                        <a
                          href={api.getEvidenceUrl(c.evidence_filename)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="badge"
                          style={{
                            background: c.evidence_filename.toLowerCase().endsWith('.pdf') ? '#fee2e2' : '#eff6ff',
                            color: c.evidence_filename.toLowerCase().endsWith('.pdf') ? '#dc2626' : '#1d4ed8',
                            border: `1px solid ${c.evidence_filename.toLowerCase().endsWith('.pdf') ? '#fca5a5' : '#bfdbfe'}`,
                            fontSize: '0.68rem',
                            padding: '1px 5px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px',
                            textDecoration: 'none'
                          }}
                          title={`Citizen attached evidence: ${c.evidence_filename}`}
                        >
                          {c.evidence_filename.toLowerCase().endsWith('.pdf') ? '📄 PDF' : '📷 Photo'}
                        </a>
                      </div>
                    )}
                    {c.manual_override && (
                      <span style={{ display: 'block', fontSize: '0.7rem', color: '#b45309' }}>
                        [Overridden]
                      </span>
                    )}
                  </td>
                  <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    {c.created_at ? c.created_at.split(' ')[0] : 'Today'}
                  </td>
                  <td>{c.category}</td>
                  <td>{c.issue_type}</td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{c.ward}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{c.location}</div>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600, color: '#1e3a8a' }}>
                      {c.department || 'Unassigned'}
                    </span>
                  </td>
                  <td>{getPriorityBadge(c.priority)}</td>
                  <td>{getEscalationBadge(c.escalation)}</td>
                  <td>
                    <span className="badge badge-neutral">{c.status}</span>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      onClick={() => onSelectComplaint(c.complaint_id)}
                      style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}
                    >
                      <Eye size={14} />
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
