import React, { useState, useEffect } from 'react';
import {
  Building,
  ShieldAlert,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Zap,
  Eye,
  RefreshCw,
  Wrench,
  PlusCircle,
  Paperclip,
  FileText,
  Image as ImageIcon,
  Send,
  Check,
  Search,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const NORMALIZE = {
  'Submitted': 'SUBMITTED',
  'SUBMITTED': 'SUBMITTED',
  'Under Review': 'ACKNOWLEDGED',
  'Assigned': 'ACKNOWLEDGED',
  'Accepted': 'ACKNOWLEDGED',
  'ACCEPTED': 'ACKNOWLEDGED',
  'ACKNOWLEDGED': 'ACKNOWLEDGED',
  'In Progress': 'IN_PROGRESS',
  'IN_PROGRESS': 'IN_PROGRESS',
  'Work Completed': 'RESOLVED',
  'WORK_COMPLETED': 'RESOLVED',
  'User Informed': 'RESOLVED',
  'USER_INFORMED': 'RESOLVED',
  'Resolved': 'RESOLVED',
  'RESOLVED': 'RESOLVED',
  'Closed': 'CLOSED',
  'CLOSED': 'CLOSED'
};

export default function OfficerDashboard({ onSelectComplaint }) {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [priorityFilter, setPriorityFilter] = useState('');
  const [stageFilter, setStageFilter] = useState('ALL'); // ALL, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, CLOSED
  const [searchQuery, setSearchQuery] = useState('');

  // Modals for Officer Responsibilities
  const [activeModal, setActiveModal] = useState(null); // 'START_WORK', 'PROGRESS_UPDATE', 'RESOLVE'
  const [selectedComp, setSelectedComp] = useState(null);
  const [actionMessage, setActionMessage] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const list = await api.getComplaints({
        priority: priorityFilter || undefined,
        search: searchQuery || undefined,
      });
      setComplaints(list || []);
    } catch (err) {
      console.error('Failed to load officer complaints', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [priorityFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  // 1. Accept / Start Work (Stage 2 -> Stage 3)
  const handleStartWorkSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp) return;
    setActionLoading(true);
    try {
      await api.startWork(selectedComp.complaint_id, actionMessage || undefined);
      setActiveModal(null);
      setSelectedComp(null);
      setActionMessage('');
      alert('Work started successfully! Citizen has been notified.');
      loadData();
    } catch (err) {
      alert(`Failed to start work: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // 2. Add Progress Update (Stage 3)
  const handleProgressUpdateSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp || !actionMessage.trim()) {
      alert('Please enter a progress update note.');
      return;
    }
    setActionLoading(true);
    try {
      await api.addProgressUpdate(selectedComp.complaint_id, actionMessage.trim());
      setActiveModal(null);
      setSelectedComp(null);
      setActionMessage('');
      alert('Progress update recorded and transmitted to citizen!');
      loadData();
    } catch (err) {
      alert(`Failed to post progress update: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // 3. Resolve Complaint (Stage 3 -> Stage 4)
  const handleResolveSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp || !actionMessage.trim()) {
      alert('Please enter a work completion / resolution description.');
      return;
    }
    setActionLoading(true);
    try {
      await api.completeWork(selectedComp.complaint_id, actionMessage.trim());
      setActiveModal(null);
      setSelectedComp(null);
      setActionMessage('');
      alert('Complaint marked RESOLVED! Municipal administration notified for formal verification and closure.');
      loadData();
    } catch (err) {
      alert(`Failed to resolve complaint: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Statistics
  const totalAssigned = complaints.length;
  const critical = complaints.filter(c => c.priority === 'CRITICAL').length;
  const high = complaints.filter(c => c.priority === 'HIGH').length;
  const stage2Count = complaints.filter(c => ['ACKNOWLEDGED', 'ACCEPTED', 'Under Review', 'Assigned'].includes(c.status)).length;
  const inProgressCount = complaints.filter(c => ['IN_PROGRESS', 'In Progress'].includes(c.status)).length;
  const resolvedCount = complaints.filter(c => ['RESOLVED', 'Resolved', 'WORK_COMPLETED', 'Work Completed', 'CLOSED', 'Closed'].includes(c.status)).length;

  // Filter complaints based on Stage Tab
  const filteredComplaints = complaints.filter(c => {
    const norm = NORMALIZE[c.status] || 'SUBMITTED';
    if (stageFilter === 'ACKNOWLEDGED') return norm === 'ACKNOWLEDGED';
    if (stageFilter === 'IN_PROGRESS') return norm === 'IN_PROGRESS';
    if (stageFilter === 'RESOLVED') return norm === 'RESOLVED';
    if (stageFilter === 'CLOSED') return norm === 'CLOSED';
    return true;
  });

  const getPriorityBadge = (p) => {
    switch (p?.toUpperCase()) {
      case 'CRITICAL': return <span className="badge badge-critical">CRITICAL</span>;
      case 'HIGH': return <span className="badge badge-high">HIGH</span>;
      case 'MEDIUM': return <span className="badge badge-medium">MEDIUM</span>;
      default: return <span className="badge badge-low">LOW</span>;
    }
  };

  const getStageBadge = (st) => {
    const norm = NORMALIZE[st] || 'SUBMITTED';
    switch (norm) {
      case 'SUBMITTED':
        return <span className="badge" style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a' }}>1. Submitted (20%)</span>;
      case 'ACKNOWLEDGED':
        return <span className="badge" style={{ background: '#e0f2fe', color: '#0369a1', border: '1px solid #bae6fd' }}>2. Acknowledged (40%)</span>;
      case 'IN_PROGRESS':
        return <span className="badge" style={{ background: '#fef9c3', color: '#a16207', border: '1px solid #fde047' }}>3. In Progress (60%)</span>;
      case 'RESOLVED':
        return <span className="badge" style={{ background: '#dcfce7', color: '#15803d', border: '1px solid #bbf7d0' }}>4. Resolved (80%)</span>;
      case 'CLOSED':
        return <span className="badge" style={{ background: '#f1f5f9', color: '#475569', border: '1px solid #cbd5e1' }}>5. Closed (100%)</span>;
      default:
        return <span className="badge badge-neutral">{st}</span>;
    }
  };

  return (
    <div>
      {/* Header Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)', color: '#ffffff', border: 'none', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.85 }}>
              Department Operations &amp; Field Remediation Queue
            </span>
            <h1 style={{ fontSize: '1.65rem', fontWeight: 800, marginTop: '0.2rem' }}>
              {user?.department_name || 'Department'} Queue
            </h1>
            <p style={{ fontSize: '0.88rem', opacity: 0.9, maxWidth: '700px', marginTop: '0.3rem' }}>
              Officer Console for <strong>{user?.name}</strong>. View assigned complaints, start work, publish field updates, and resolve grievances.
            </p>
          </div>
          <span className="badge badge-primary" style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: '#ffffff', border: '1px solid rgba(255,255,255,0.3)', padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
            Role: Department Officer
          </span>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-box primary">
          <span className="stat-label">Assigned Complaints</span>
          <div className="stat-value">{totalAssigned}</div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>In {user?.department_name || 'department'}</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #0284c7' }}>
          <span className="stat-label">Ready for Field Work</span>
          <div className="stat-value" style={{ color: '#0284c7' }}>{stage2Count}</div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Stage 2: Acknowledged</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #d97706' }}>
          <span className="stat-label">In Progress</span>
          <div className="stat-value" style={{ color: '#d97706' }}>{inProgressCount}</div>
          <span style={{ fontSize: '0.75rem', color: '#d97706' }}>Active field teams</span>
        </div>

        <div className="stat-box low">
          <span className="stat-label">Resolved Work</span>
          <div className="stat-value" style={{ color: '#15803d' }}>{resolvedCount}</div>
          <span style={{ fontSize: '0.75rem', color: '#15803d' }}>Completed remediation</span>
        </div>

        <div className="stat-box critical">
          <span className="stat-label">Critical Hazards</span>
          <div className="stat-value" style={{ color: '#b91c1c' }}>{critical}</div>
          <span style={{ fontSize: '0.75rem', color: '#b91c1c' }}>Priority SLA clock</span>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <Building size={18} />
              Assigned Department Grievances ({filteredComplaints.length})
            </h2>
            <p className="card-subtitle">
              Strictly filtered to complaints routed to <strong>{user?.department_name || 'your department'}</strong>.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            Refresh
          </button>
        </div>

        {/* 5-Stage Filter Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
          <button
            className={`btn ${stageFilter === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            onClick={() => setStageFilter('ALL')}
          >
            All Assigned ({complaints.length})
          </button>
          <button
            className={`btn ${stageFilter === 'ACKNOWLEDGED' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            onClick={() => setStageFilter('ACKNOWLEDGED')}
          >
            Stage 2: Acknowledged ({stage2Count})
          </button>
          <button
            className={`btn ${stageFilter === 'IN_PROGRESS' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            onClick={() => setStageFilter('IN_PROGRESS')}
          >
            Stage 3: In Progress ({inProgressCount})
          </button>
          <button
            className={`btn ${stageFilter === 'RESOLVED' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            onClick={() => setStageFilter('RESOLVED')}
          >
            Stage 4: Resolved ({complaints.filter(c => NORMALIZE[c.status] === 'RESOLVED').length})
          </button>
          <button
            className={`btn ${stageFilter === 'CLOSED' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            onClick={() => setStageFilter('CLOSED')}
          >
            Stage 5: Closed ({complaints.filter(c => NORMALIZE[c.status] === 'CLOSED').length})
          </button>
        </div>

        {/* Search & Priority Controls */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.4rem', flex: 1, minWidth: '240px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by Ticket ID, citizen, ward, or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="btn btn-secondary" style={{ padding: '0.5rem 0.75rem' }}>
              <Search size={15} />
            </button>
          </form>

          <select
            className="form-select"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>

        {/* Complaints Table */}
        {filteredComplaints.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
            No assigned complaints found matching the selected filters.
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket ID &amp; Evidence</th>
                  <th>Citizen</th>
                  <th>Location</th>
                  <th>Issue &amp; Category</th>
                  <th>Priority</th>
                  <th>Current Stage</th>
                  <th>Officer Action</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {filteredComplaints.map((c) => {
                  const normSt = NORMALIZE[c.status] || 'SUBMITTED';
                  const isPdf = c.evidence_filename?.toLowerCase().endsWith('.pdf');
                  return (
                    <tr key={c.complaint_id}>
                      <td>
                        <strong>{c.complaint_id}</strong>
                        {/* Attachment indicator visible to officer */}
                        {c.evidence_filename && (
                          <div style={{ marginTop: '0.25rem' }}>
                            <a
                              href={api.getEvidenceUrl(c.evidence_filename)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="badge"
                              style={{
                                background: isPdf ? '#fee2e2' : '#eff6ff',
                                color: isPdf ? '#dc2626' : '#1d4ed8',
                                border: `1px solid ${isPdf ? '#fca5a5' : '#bfdbfe'}`,
                                fontSize: '0.68rem',
                                padding: '1px 6px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '3px',
                                textDecoration: 'none',
                                cursor: 'pointer'
                              }}
                              title={`Click to view attached evidence: ${c.evidence_filename}`}
                            >
                              {isPdf ? <FileText size={11} /> : <ImageIcon size={11} />}
                              {isPdf ? 'PDF Evidence' : 'Photo Attached'}
                              <ExternalLink size={9} />
                            </a>
                          </div>
                        )}
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{c.citizen_name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{c.phone}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{c.ward}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{c.location}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, color: '#1e3a8a' }}>{c.issue_type}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{c.category}</div>
                      </td>
                      <td>{getPriorityBadge(c.priority)}</td>
                      <td>{getStageBadge(c.status)}</td>
                      <td>
                        {/* Exact Officer Responsibilities based on stage */}
                        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                          {/* Stage 2: Accept / Start Work */}
                          {normSt === 'ACKNOWLEDGED' && (
                            <button
                              className="btn btn-primary"
                              style={{ fontSize: '0.74rem', padding: '0.25rem 0.55rem', background: '#2563eb', borderColor: '#2563eb', fontWeight: 700 }}
                              onClick={() => {
                                setSelectedComp(c);
                                setActiveModal('START_WORK');
                              }}
                              title="Accept grievance and dispatch field crew"
                            >
                              <Wrench size={13} /> Start Work
                            </button>
                          )}

                          {/* Stage 3: Add Updates & Resolve */}
                          {normSt === 'IN_PROGRESS' && (
                            <>
                              <button
                                className="btn btn-secondary"
                                style={{ fontSize: '0.74rem', padding: '0.25rem 0.55rem', fontWeight: 600 }}
                                onClick={() => {
                                  setSelectedComp(c);
                                  setActiveModal('PROGRESS_UPDATE');
                                }}
                                title="Add field inspection / progress update"
                              >
                                <PlusCircle size={13} /> Add Update
                              </button>
                              <button
                                className="btn btn-primary"
                                style={{ fontSize: '0.74rem', padding: '0.25rem 0.55rem', background: '#16a34a', borderColor: '#16a34a', fontWeight: 700 }}
                                onClick={() => {
                                  setSelectedComp(c);
                                  setActiveModal('RESOLVE');
                                }}
                                title="Mark physical work completed & resolved"
                              >
                                <CheckCircle2 size={13} /> Resolve
                              </button>
                            </>
                          )}

                          {/* Stage 4: Resolved */}
                          {normSt === 'RESOLVED' && (
                            <span style={{ fontSize: '0.74rem', color: '#15803d', fontWeight: 600 }}>
                              ✓ Awaiting Admin Closure
                            </span>
                          )}

                          {/* Stage 5: Closed */}
                          {normSt === 'CLOSED' && (
                            <span style={{ fontSize: '0.74rem', color: '#64748b' }}>
                              Archived &bull; Closed
                            </span>
                          )}

                          {/* Stage 1: Submitted */}
                          {normSt === 'SUBMITTED' && (
                            <span style={{ fontSize: '0.74rem', color: '#92400e' }}>
                              Awaiting Admin Ack
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '0.74rem', padding: '0.25rem 0.55rem' }}
                          onClick={() => onSelectComplaint(c.complaint_id)}
                          title="View complete particulars, evidence, and flowchart"
                        >
                          <Eye size={13} /> View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ============================================================== */}
      {/* OFFICER INTERACTIVE ACTION MODALS */}
      {/* ============================================================== */}

      {/* Modal 1: Start Work (Stage 2 -> Stage 3) */}
      {activeModal === 'START_WORK' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div className="card" style={{ width: '520px', maxWidth: '100%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', color: '#1e3a8a' }}>
                <Wrench size={18} color="#2563eb" />
                Start Work on #{selectedComp.complaint_id}
              </h3>
              <button className="btn btn-secondary" onClick={() => { setActiveModal(null); setSelectedComp(null); }}>✕</button>
            </div>
            <form onSubmit={handleStartWorkSubmit}>
              <p style={{ fontSize: '0.86rem', color: '#475569', marginBottom: '1rem' }}>
                You are dispatching field operations for <strong>{selectedComp.issue_type}</strong> in {selectedComp.ward}. The ticket will advance to <strong>IN_PROGRESS</strong>.
              </p>
              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label">Dispatch Notice / Work Commencement Message (Sent to Citizen)</label>
                <textarea
                  className="form-input"
                  rows="3"
                  placeholder="e.g. Field inspection crew dispatched to site. Work started on restoring road pavement."
                  value={actionMessage}
                  onChange={(e) => setActionMessage(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => { setActiveModal(null); setSelectedComp(null); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#2563eb', borderColor: '#2563eb', fontWeight: 700 }} disabled={actionLoading}>
                  {actionLoading ? 'Starting Work...' : 'Confirm & Start Work'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: Add Progress Update (Stage 3) */}
      {activeModal === 'PROGRESS_UPDATE' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div className="card" style={{ width: '520px', maxWidth: '100%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', color: '#1e3a8a' }}>
                <PlusCircle size={18} color="#0284c7" />
                Add Progress Update: #{selectedComp.complaint_id}
              </h3>
              <button className="btn btn-secondary" onClick={() => { setActiveModal(null); setSelectedComp(null); }}>✕</button>
            </div>
            <form onSubmit={handleProgressUpdateSubmit}>
              <p style={{ fontSize: '0.86rem', color: '#475569', marginBottom: '1rem' }}>
                Publish an operational status update for the citizen and municipal log.
              </p>
              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label">Progress Report / Field Findings *</label>
                <textarea
                  className="form-input"
                  rows="4"
                  placeholder="e.g. Excavation complete. Replacement 300mm pipe delivered to site. Welding scheduled for 2 PM."
                  value={actionMessage}
                  onChange={(e) => setActionMessage(e.target.value)}
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => { setActiveModal(null); setSelectedComp(null); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#0284c7', borderColor: '#0284c7', fontWeight: 700 }} disabled={actionLoading}>
                  {actionLoading ? 'Publishing...' : 'Publish Progress Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 3: Resolve Complaint (Stage 3 -> Stage 4) */}
      {activeModal === 'RESOLVE' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div className="card" style={{ width: '520px', maxWidth: '100%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', color: '#166534' }}>
                <CheckCircle2 size={18} color="#16a34a" />
                Mark Resolved: #{selectedComp.complaint_id}
              </h3>
              <button className="btn btn-secondary" onClick={() => { setActiveModal(null); setSelectedComp(null); }}>✕</button>
            </div>
            <form onSubmit={handleResolveSubmit}>
              <p style={{ fontSize: '0.86rem', color: '#475569', marginBottom: '1rem' }}>
                Declare that physical remediation for <strong>{selectedComp.issue_type}</strong> has concluded. The grievance will advance to <strong>RESOLVED (80%)</strong>.
              </p>
              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label">Resolution Summary (Transmitted to Citizen &amp; Admin) *</label>
                <textarea
                  className="form-input"
                  rows="4"
                  placeholder="e.g. Field crew completed transformer repair; electrical supply fully restored and safety inspected."
                  value={actionMessage}
                  onChange={(e) => setActionMessage(e.target.value)}
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => { setActiveModal(null); setSelectedComp(null); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#16a34a', borderColor: '#16a34a', fontWeight: 700 }} disabled={actionLoading}>
                  {actionLoading ? 'Marking Resolved...' : 'Confirm Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
