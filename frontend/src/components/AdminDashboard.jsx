import React, { useState, useEffect } from 'react';
import {
  Users,
  Shield,
  Building,
  AlertTriangle,
  Zap,
  CheckCircle2,
  Clock,
  ArrowRight,
  History,
  TrendingUp,
  Send,
  Eye,
  Check,
  Sparkles,
  BarChart3,
  AlertCircle,
  Wrench,
  Layers,
  RefreshCw,
  FileCheck2,
  Activity,
  Lock,
  PlusCircle
} from 'lucide-react';
import api from '../services/api';

const NORMALIZE = {
  'Submitted': 'SUBMITTED',
  'SUBMITTED': 'SUBMITTED',
  'Under Review': 'ACKNOWLEDGED',
  'ACKNOWLEDGED': 'ACKNOWLEDGED',
  'Assigned': 'ACKNOWLEDGED',
  'Accepted': 'ACKNOWLEDGED',
  'ACCEPTED': 'ACKNOWLEDGED',
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

export default function AdminDashboard({ onNavigate, onSelectComplaint }) {
  const [stats, setStats] = useState(null);
  const [allComplaints, setAllComplaints] = useState([]);
  const [pendingComplaints, setPendingComplaints] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stageFilter, setStageFilter] = useState('ALL');

  // Modals state: 'ACCEPT', 'START_WORK', 'PROGRESS', 'COMPLETE', 'INFORM', 'CLOSE'
  const [activeModal, setActiveModal] = useState(null);
  const [selectedComp, setSelectedComp] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  // Form input states
  const [assignDept, setAssignDept] = useState('');
  const [assignPriority, setAssignPriority] = useState('MEDIUM');
  const [assignMessage, setAssignMessage] = useState('');
  const [startWorkMsg, setStartWorkMsg] = useState('');
  const [progressMsg, setProgressMsg] = useState('');
  const [completeMsg, setCompleteMsg] = useState('');
  const [informMsg, setInformMsg] = useState('');
  const [closeMsg, setCloseMsg] = useState('');

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [dashData, compList, deptList] = await Promise.all([
        api.getDashboard(),
        api.getComplaints(),
        api.getDepartments(),
      ]);
      setStats(dashData);
      setAllComplaints(compList);
      setPendingComplaints(compList.filter(c => ['SUBMITTED', 'ACKNOWLEDGED', 'Submitted', 'Under Review'].includes(c.status)));
      setDepartments(deptList);
      if (deptList.length > 0 && !assignDept) {
        setAssignDept(deptList[0].name);
      }
    } catch (err) {
      console.error('Failed to load admin dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  // Quick Action: Acknowledge (Section 74)
  const handleAcknowledge = async (comp) => {
    try {
      await api.acknowledgeComplaint(comp.complaint_id);
      await loadAdminData();
      alert(`Complaint #${comp.complaint_id} acknowledged.`);
    } catch (err) {
      alert(`Acknowledgement failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  // Open Accept Modal (Section 75 & 76)
  const openAcceptModal = (comp) => {
    setSelectedComp(comp);
    const dept = comp.ai_department || comp.department || (departments[0]?.name || '');
    setAssignDept(dept);
    setAssignPriority(comp.priority || 'MEDIUM');
    setAssignMessage(
      `Your complaint #${comp.complaint_id} has been reviewed and accepted. The concerned department has been instructed to take necessary action.`
    );
    setActiveModal('ACCEPT');
  };

  const handleAcceptSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp || !assignMessage.trim()) return;
    setModalLoading(true);
    try {
      // If currently submitted, acknowledge first if needed
      const normSt = NORMALIZE[selectedComp.status] || 'SUBMITTED';
      if (normSt === 'SUBMITTED') {
        await api.acknowledgeComplaint(selectedComp.complaint_id, 'Acknowledged during review.');
      }
      await api.acceptComplaint(selectedComp.complaint_id, {
        department: assignDept,
        priority: assignPriority,
        message: assignMessage.trim()
      });
      setActiveModal(null);
      await loadAdminData();
      alert(`Complaint #${selectedComp.complaint_id} accepted.`);
    } catch (err) {
      alert(`Acceptance failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setModalLoading(false);
    }
  };

  // Start Work (Section 77)
  const openStartWorkModal = (comp) => {
    setSelectedComp(comp);
    setStartWorkMsg('The maintenance team has been assigned and inspection has started.');
    setActiveModal('START_WORK');
  };

  const handleStartWorkSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp) return;
    setModalLoading(true);
    try {
      await api.startWork(selectedComp.complaint_id, startWorkMsg.trim());
      setActiveModal(null);
      await loadAdminData();
      alert(`Work started on #${selectedComp.complaint_id}.`);
    } catch (err) {
      alert(`Failed to start work: ${err.response?.data?.detail || err.message}`);
    } finally {
      setModalLoading(false);
    }
  };

  // Progress Update (Section 78)
  const openProgressModal = (comp) => {
    setSelectedComp(comp);
    setProgressMsg('');
    setActiveModal('PROGRESS');
  };

  const handleProgressSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp || !progressMsg.trim()) return;
    setModalLoading(true);
    try {
      await api.addProgressUpdate(selectedComp.complaint_id, progressMsg.trim());
      setActiveModal(null);
      await loadAdminData();
      alert(`Progress update added for #${selectedComp.complaint_id}.`);
    } catch (err) {
      alert(`Failed to add update: ${err.response?.data?.detail || err.message}`);
    } finally {
      setModalLoading(false);
    }
  };

  // Complete Work (Section 79)
  const openCompleteModal = (comp) => {
    setSelectedComp(comp);
    setCompleteMsg('Field crew completed required repairs. System restored to normal operational state.');
    setActiveModal('COMPLETE');
  };

  const handleCompleteSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp || !completeMsg.trim()) return;
    setModalLoading(true);
    try {
      await api.completeWork(selectedComp.complaint_id, completeMsg.trim());
      setActiveModal(null);
      await loadAdminData();
      alert(`Work completed on #${selectedComp.complaint_id}. Next step: Inform citizen of resolution.`);
    } catch (err) {
      alert(`Failed to complete work: ${err.response?.data?.detail || err.message}`);
    } finally {
      setModalLoading(false);
    }
  };

  // Inform User (Section 80)
  const openInformModal = (comp) => {
    setSelectedComp(comp);
    setInformMsg('Your complaint has been resolved. Please review the completion details.');
    setActiveModal('INFORM');
  };

  const handleInformSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp || !informMsg.trim()) return;
    setModalLoading(true);
    try {
      await api.informUser(selectedComp.complaint_id, informMsg.trim());
      setActiveModal(null);
      await loadAdminData();
      alert(`Citizen informed of resolution for #${selectedComp.complaint_id}. Ticket can now be closed.`);
    } catch (err) {
      alert(`Failed to inform citizen: ${err.response?.data?.detail || err.message}`);
    } finally {
      setModalLoading(false);
    }
  };

  // Close Complaint (Section 81)
  const openCloseModal = (comp) => {
    setSelectedComp(comp);
    setCloseMsg('Complaint lifecycle formally closed by administration.');
    setActiveModal('CLOSE');
  };

  const handleCloseSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComp) return;
    if (!window.confirm(`Are you sure you want to close complaint #${selectedComp.complaint_id}?`)) return;
    setModalLoading(true);
    try {
      await api.closeComplaint(selectedComp.complaint_id, closeMsg.trim());
      setActiveModal(null);
      await loadAdminData();
      alert(`Complaint #${selectedComp.complaint_id} formally closed.`);
    } catch (err) {
      alert(`Failed to close complaint: ${err.response?.data?.detail || err.message}`);
    } finally {
      setModalLoading(false);
    }
  };

  if (loading && !stats) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <RefreshCw className="spin" size={32} color="#1e3a8a" style={{ margin: '0 auto 1rem auto' }} />
        <p style={{ fontWeight: 600, color: '#475569' }}>Loading Municipal Administration Command Center...</p>
      </div>
    );
  }

  const total = stats?.total_complaints || allComplaints.length;
  const queues = stats?.queues || {};

  // Filter complaints according to stageFilter (Section 85)
  const filteredComplaints = allComplaints.filter(c => {
    if (stageFilter === 'ALL') return true;
    const norm = NORMALIZE[c.status] || 'SUBMITTED';
    return norm === stageFilter;
  });

  const getPriorityBadge = (p) => {
    switch (p?.toUpperCase()) {
      case 'CRITICAL': return <span className="badge badge-critical">CRITICAL</span>;
      case 'HIGH': return <span className="badge badge-high">HIGH</span>;
      case 'MEDIUM': return <span className="badge badge-medium">MEDIUM</span>;
      default: return <span className="badge badge-low">LOW</span>;
    }
  };

  const getStatusBadge = (status) => {
    const s = NORMALIZE[status] || 'SUBMITTED';
    switch (s) {
      case 'CLOSED':
        return <span className="badge badge-low" style={{ fontWeight: 700 }}>✓ Closed</span>;
      case 'RESOLVED':
        return <span className="badge" style={{ background: '#dcfce7', color: '#15803d', fontWeight: 700 }}>Resolved</span>;
      case 'IN_PROGRESS':
        return <span className="badge badge-high">Work in Progress</span>;
      case 'ACKNOWLEDGED':
        return <span className="badge" style={{ background: '#fef3c7', color: '#b45309', fontWeight: 600 }}>Acknowledged</span>;
      default:
        return <span className="badge badge-med">Submitted</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', color: '#ffffff', border: 'none', marginBottom: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38bdf8', fontWeight: 700 }}>
                Municipal Administration Console
              </span>
              <span style={{ background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', fontSize: '0.7rem', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                5-Stage State Machine Active
              </span>
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
              Grievance Governance &amp; AI Decision Dashboard
            </h1>
            <p style={{ fontSize: '0.88rem', opacity: 0.85, maxWidth: '750px', marginTop: '0.25rem' }}>
              Full 5-stage lifecycle governance: <strong>Submitted &rarr; Acknowledged &rarr; In Progress &rarr; Resolved &rarr; Closed</strong>.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button className="btn btn-secondary" onClick={loadAdminData} title="Refresh data">
              <RefreshCw size={14} /> Refresh
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate('users')}>
              <Users size={14} /> Users
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate('departments')}>
              <Building size={14} /> Departments
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate('audit-logs')}>
              <History size={14} /> Audit Logs
            </button>
          </div>
        </div>
      </div>

      {/* ============================================================== */}
      {/* 1. ADMIN WORK QUEUES & OVERVIEW (Section 85 & 91) */}
      {/* ============================================================== */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
          <div style={{ background: '#1e3a8a', color: '#ffffff', width: '28px', height: '28px', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.9rem' }}>
            1
          </div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            Operational Work Queues
          </h2>
          <span style={{ fontSize: '0.8rem', color: '#64748b', marginLeft: 'auto' }}>
            Actions requiring administrator intervention
          </span>
        </div>

        <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
          {/* Queue 1: Require Acknowledgment */}
          <div
            className="stat-box"
            style={{ borderLeft: '4px solid #f59e0b', background: '#fffbeb', cursor: 'pointer' }}
            onClick={() => setStageFilter('SUBMITTED')}
          >
            <span className="stat-label" style={{ color: '#b45309' }}>1. Require Acknowledgement</span>
            <div className="stat-value" style={{ color: '#d97706' }}>{queues.requiring_acknowledgement ?? (stats?.submitted_complaints || 0)}</div>
            <span style={{ fontSize: '0.72rem', color: '#b45309' }}>Newly submitted complaints</span>
          </div>

          {/* Queue 2: Require Acceptance */}
          <div
            className="stat-box"
            style={{ borderLeft: '4px solid #7c3aed', background: '#faf5ff', cursor: 'pointer' }}
            onClick={() => setStageFilter('ACKNOWLEDGED')}
          >
            <span className="stat-label" style={{ color: '#6d28d9' }}>2. Require Acceptance</span>
            <div className="stat-value" style={{ color: '#7c3aed' }}>{queues.requiring_acceptance ?? (stats?.acknowledged_complaints || 0)}</div>
            <span style={{ fontSize: '0.72rem', color: '#6d28d9' }}>Acknowledged &amp; AI-reviewed</span>
          </div>

          {/* Queue 3: Work Not Started */}
          <div
            className="stat-box"
            style={{ borderLeft: '4px solid #0f766e', background: '#f0fdfa', cursor: 'pointer' }}
            onClick={() => setStageFilter('ACCEPTED')}
          >
            <span className="stat-label" style={{ color: '#0f766e' }}>3. Work Not Started</span>
            <div className="stat-value" style={{ color: '#0f766e' }}>{queues.work_not_started ?? (stats?.accepted_complaints || 0)}</div>
            <span style={{ fontSize: '0.72rem', color: '#0f766e' }}>Accepted / Dispatched</span>
          </div>

          {/* Queue 4: In Progress */}
          <div
            className="stat-box"
            style={{ borderLeft: '4px solid #2563eb', background: '#eff6ff', cursor: 'pointer' }}
            onClick={() => setStageFilter('IN_PROGRESS')}
          >
            <span className="stat-label" style={{ color: '#1e40af' }}>4. Active Field Work</span>
            <div className="stat-value" style={{ color: '#2563eb' }}>{queues.currently_in_progress ?? (stats?.in_progress_complaints || 0)}</div>
            <span style={{ fontSize: '0.72rem', color: '#1e40af' }}>Maintenance underway</span>
          </div>

          {/* Queue 5: Awaiting User Notification */}
          <div
            className="stat-box"
            style={{ borderLeft: '4px solid #10b981', background: '#ecfdf5', cursor: 'pointer' }}
            onClick={() => setStageFilter('WORK_COMPLETED')}
          >
            <span className="stat-label" style={{ color: '#065f46' }}>5. Awaiting User Notice</span>
            <div className="stat-value" style={{ color: '#059669' }}>{queues.awaiting_user_notification ?? (stats?.work_completed_complaints || 0)}</div>
            <span style={{ fontSize: '0.72rem', color: '#065f46' }}>Work done, citizen not informed</span>
          </div>

          {/* Queue 6: Awaiting Closure */}
          <div
            className="stat-box"
            style={{ borderLeft: '4px solid #15803d', background: '#f0fdf4', cursor: 'pointer' }}
            onClick={() => setStageFilter('USER_INFORMED')}
          >
            <span className="stat-label" style={{ color: '#166534' }}>6. Awaiting Closure</span>
            <div className="stat-value" style={{ color: '#15803d' }}>{queues.awaiting_closure ?? (stats?.user_informed_complaints || 0)}</div>
            <span style={{ fontSize: '0.72rem', color: '#166534' }}>Citizen informed, ready to close</span>
          </div>
        </div>
      </div>

      {/* ============================================================== */}
      {/* 2. AI RECOMMENDATIONS & INCOMING COMPLAINTS (Section 74 & 75) */}
      {/* ============================================================== */}
      <div className="card" style={{ border: '2px solid #7c3aed', background: '#faf5ff' }}>
        <div className="card-header" style={{ borderBottomColor: '#ede9fe', paddingBottom: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <div style={{ background: '#7c3aed', color: '#ffffff', width: '28px', height: '28px', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.9rem' }}>
                2
              </div>
              <h2 className="card-title" style={{ color: '#6d28d9', fontSize: '1.25rem' }}>
                <Sparkles size={20} color="#7c3aed" />
                AI Recommendations &amp; Incoming Review Queue
              </h2>
            </div>
            <p className="card-subtitle" style={{ color: '#6b21a8' }}>
              Review newly filed complaints, acknowledge receipt in 1-click, and accept tickets with custom response messages sent to citizens.
            </p>
          </div>
          <span className="badge" style={{ background: pendingComplaints.length > 0 ? '#7c3aed' : '#16a34a', color: '#ffffff', fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}>
            {pendingComplaints.length} Pending Review
          </span>
        </div>

        {pendingComplaints.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #ede9fe' }}>
            <CheckCircle2 size={32} color="#16a34a" style={{ margin: '0 auto 0.5rem auto' }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>All Incoming Complaints Have Been Processed!</h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '0.2rem' }}>
              New grievances filed by citizens will automatically appear here for acknowledgement and acceptance.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginTop: '0.5rem' }}>
            {pendingComplaints.map((c) => {
              const recDept = c.ai_department || c.department || 'Road Maintenance';
              const normSt = NORMALIZE[c.status] || 'SUBMITTED';
              return (
                <div
                  key={c.complaint_id}
                  style={{
                    background: '#ffffff',
                    border: '1.5px solid #ddd6fe',
                    borderRadius: '8px',
                    padding: '1rem',
                    boxShadow: 'var(--shadow-sm)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <strong style={{ fontSize: '1rem', color: '#1e3a8a' }}>#{c.complaint_id}</strong>
                        <span style={{ fontSize: '0.82rem', color: '#64748b' }}>&bull; {c.citizen_name} ({c.phone})</span>
                        <span className="badge" style={{ background: normSt === 'SUBMITTED' ? '#fef3c7' : '#ccfbf1', color: normSt === 'SUBMITTED' ? '#b45309' : '#0f766e', fontWeight: 700, fontSize: '0.72rem' }}>
                          {normSt === 'SUBMITTED' ? 'Stage 1: SUBMITTED' : 'Stage 2: ACKNOWLEDGED'}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#0f172a', marginTop: '0.25rem' }}>
                        {c.category} &rarr; {c.issue_type} in {c.ward}
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      {normSt === 'SUBMITTED' && (
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem', color: '#b45309', borderColor: '#f59e0b' }}
                          onClick={() => handleAcknowledge(c)}
                        >
                          <Check size={14} /> 1. Acknowledge
                        </button>
                      )}
                      <button
                        className="btn btn-primary"
                        style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem', background: '#7c3aed', borderColor: '#7c3aed' }}
                        onClick={() => openAcceptModal(c)}
                      >
                        <Send size={14} /> 2. Accept &amp; Dispatch
                      </button>
                      <button
                        className="btn btn-secondary"
                        style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}
                        onClick={() => onSelectComplaint(c.complaint_id)}
                      >
                        <Eye size={14} /> Inspect
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ============================================================== */}
      {/* 3. SEPARATE VIEWS & COMPLAINT MANAGEMENT (Section 85 & 86) */}
      {/* ============================================================== */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h3 className="card-title">
              <Clock size={18} />
              Grievance Lifecycle Management
            </h3>
            <p className="card-subtitle">
              Separate views by lifecycle stage. Actions are constrained strictly to valid state transitions.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={() => onNavigate('history')}>
            Advanced Search &rarr;
          </button>
        </div>

        {/* 5 View Tabs */}
        <div style={{ display: 'flex', gap: '0.4rem', overflowX: 'auto', paddingBottom: '0.5rem', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0' }}>
          {[
            { id: 'ALL', label: 'All Complaints', count: allComplaints.length },
            { id: 'SUBMITTED', label: '1. New', count: allComplaints.filter(c => NORMALIZE[c.status] === 'SUBMITTED').length },
            { id: 'ACKNOWLEDGED', label: '2. Acknowledged', count: allComplaints.filter(c => NORMALIZE[c.status] === 'ACKNOWLEDGED').length },
            { id: 'IN_PROGRESS', label: '3. In Progress', count: allComplaints.filter(c => NORMALIZE[c.status] === 'IN_PROGRESS').length },
            { id: 'RESOLVED', label: '4. Resolved', count: allComplaints.filter(c => NORMALIZE[c.status] === 'RESOLVED').length },
            { id: 'CLOSED', label: '5. Closed', count: allComplaints.filter(c => NORMALIZE[c.status] === 'CLOSED').length },
          ].map(tab => (
            <button
              key={tab.id}
              className="btn"
              style={{
                fontSize: '0.8rem',
                padding: '0.35rem 0.65rem',
                background: stageFilter === tab.id ? '#0f766e' : '#f1f5f9',
                color: stageFilter === tab.id ? '#ffffff' : '#334155',
                border: 'none',
                fontWeight: stageFilter === tab.id ? 700 : 500
              }}
              onClick={() => setStageFilter(tab.id)}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>

        {/* Complaints Table with State-Dependent Action Buttons (Section 86) */}
        {filteredComplaints.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
            No complaints currently in stage '{stageFilter}'.
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket ID</th>
                  <th>Citizen</th>
                  <th>Issue &amp; Category</th>
                  <th>Department</th>
                  <th>Priority</th>
                  <th>Stage</th>
                  <th>Allowed State Actions</th>
                  <th>Trace</th>
                </tr>
              </thead>
              <tbody>
                {filteredComplaints.map((c) => {
                  const normSt = NORMALIZE[c.status] || 'SUBMITTED';
                  return (
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
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{c.citizen_name}</div>
                        <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{c.ward}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, color: '#1e3a8a' }}>{c.issue_type}</div>
                        <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{c.category}</div>
                      </td>
                      <td>
                        <span style={{ fontWeight: 600, color: c.department ? '#0f766e' : '#b45309' }}>
                          {c.department || 'Pending'}
                        </span>
                      </td>
                      <td>{getPriorityBadge(c.priority)}</td>
                      <td>{getStatusBadge(c.status)}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                          {/* If SUBMITTED -> [ACKNOWLEDGE] */}
                          {normSt === 'SUBMITTED' && (
                            <button
                              className="btn btn-primary"
                              style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem', background: '#f59e0b', borderColor: '#f59e0b', color: '#000000', fontWeight: 700 }}
                              onClick={() => handleAcknowledge(c)}
                            >
                              [ACKNOWLEDGE]
                            </button>
                          )}

                          {/* If ACKNOWLEDGED -> Admin has routed to department, awaiting Officer */}
                          {normSt === 'ACKNOWLEDGED' && (
                            <span
                              style={{
                                fontSize: '0.74rem',
                                color: '#1d4ed8',
                                fontWeight: 600,
                                background: '#eff6ff',
                                padding: '0.25rem 0.5rem',
                                borderRadius: '4px',
                                border: '1px solid #bfdbfe',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '3px'
                              }}
                              title="Complaint acknowledged and routed. Awaiting Department Officer to start work."
                            >
                              ⏳ Awaiting Officer Start
                            </span>
                          )}

                          {/* If IN_PROGRESS -> Department Officer is executing field work */}
                          {normSt === 'IN_PROGRESS' && (
                            <span
                              style={{
                                fontSize: '0.74rem',
                                color: '#0369a1',
                                fontWeight: 600,
                                background: '#f0f9ff',
                                padding: '0.25rem 0.5rem',
                                borderRadius: '4px',
                                border: '1px solid #bae6fd',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '3px'
                              }}
                              title="Department Officer and field crew currently executing remediation."
                            >
                              🔧 Officer In Field
                            </span>
                          )}

                          {/* If RESOLVED -> Admin Verifies and Closes */}
                          {normSt === 'RESOLVED' && (
                            <button
                              className="btn btn-primary"
                              style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem', background: '#334155', borderColor: '#334155', fontWeight: 700 }}
                              onClick={() => openCloseModal(c)}
                              title="Department Officer has resolved this issue. Admin verifies remediation and closes complaint."
                            >
                              [VERIFY & CLOSE]
                            </button>
                          )}

                          {/* If CLOSED -> COMPLAINT CLOSED */}
                          {normSt === 'CLOSED' && (
                            <span style={{ fontSize: '0.75rem', color: '#166534', fontWeight: 700 }}>
                              ✓ COMPLAINT CLOSED
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                          onClick={() => onSelectComplaint(c.complaint_id)}
                        >
                          <Eye size={13} />
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
      {/* ACTION MODALS */}
      {/* ============================================================== */}

      {/* Accept Complaint Modal */}
      {activeModal === 'ACCEPT' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '560px', maxWidth: '92%', margin: 0, borderTop: '4px solid #7c3aed' }}>
            <div className="card-header">
              <h3 className="card-title" style={{ color: '#6d28d9' }}>Accept Grievance #{selectedComp.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleAcceptSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div style={{ background: '#f5f3ff', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                <p><strong>Citizen:</strong> {selectedComp.citizen_name} ({selectedComp.phone})</p>
                <p><strong>Location:</strong> {selectedComp.location} ({selectedComp.ward})</p>
                <p><strong>Issue:</strong> {selectedComp.issue_type} &bull; <strong>AI Dept:</strong> {selectedComp.ai_department || selectedComp.department}</p>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Assign Department *</label>
                  <select className="form-select" value={assignDept} onChange={(e) => setAssignDept(e.target.value)} required>
                    {departments.map((d) => (
                      <option key={d.department_id} value={d.name}>{d.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Priority Level *</label>
                  <select className="form-select" value={assignPriority} onChange={(e) => setAssignPriority(e.target.value)} required>
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" style={{ fontWeight: 700, color: '#0f766e' }}>
                  📩 Official Response / Description Sent to Citizen *
                </label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={assignMessage}
                  onChange={(e) => setAssignMessage(e.target.value)}
                  placeholder="Enter acceptance message sent to citizen..."
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#7c3aed', borderColor: '#7c3aed' }} disabled={modalLoading}>
                  {modalLoading ? 'Accepting...' : 'Accept Complaint & Notify Citizen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Start Work Modal */}
      {activeModal === 'START_WORK' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0, borderTop: '4px solid #2563eb' }}>
            <div className="card-header">
              <h3 className="card-title">Start Work: #{selectedComp.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleStartWorkSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Work Started Description (Sent to Citizen)</label>
                <textarea
                  className="form-input"
                  rows="2"
                  value={startWorkMsg}
                  onChange={(e) => setStartWorkMsg(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={modalLoading}>
                  {modalLoading ? 'Starting...' : 'Confirm Work Started'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Progress Update Modal */}
      {activeModal === 'PROGRESS' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Add Progress Update: #{selectedComp.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleProgressSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Progress Update Message *</label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={progressMsg}
                  onChange={(e) => setProgressMsg(e.target.value)}
                  placeholder="e.g. Inspection completed; spare component arriving today."
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={modalLoading}>
                  {modalLoading ? 'Saving...' : 'Publish Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Complete Work Modal */}
      {activeModal === 'COMPLETE' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '540px', maxWidth: '90%', margin: 0, borderTop: '4px solid #16a34a' }}>
            <div className="card-header">
              <h3 className="card-title">Mark Work Completed: #{selectedComp.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleCompleteSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Work Completion Description *</label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={completeMsg}
                  onChange={(e) => setCompleteMsg(e.target.value)}
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#16a34a', borderColor: '#16a34a' }} disabled={modalLoading}>
                  {modalLoading ? 'Saving...' : 'Confirm Work Completed'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Inform User Modal */}
      {activeModal === 'INFORM' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '540px', maxWidth: '90%', margin: 0, borderTop: '4px solid #0f766e' }}>
            <div className="card-header">
              <h3 className="card-title">Inform Citizen of Resolution: #{selectedComp.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleInformSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Resolution Notice to Citizen *</label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={informMsg}
                  onChange={(e) => setInformMsg(e.target.value)}
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#0f766e', borderColor: '#0f766e' }} disabled={modalLoading}>
                  {modalLoading ? 'Informing...' : 'Send Resolution Notice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Close Complaint Modal */}
      {activeModal === 'CLOSE' && selectedComp && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0, borderTop: '4px solid #334155' }}>
            <div className="card-header">
              <h3 className="card-title">Close Grievance #{selectedComp.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleCloseSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Closure Summary Notes</label>
                <textarea
                  className="form-input"
                  rows="2"
                  value={closeMsg}
                  onChange={(e) => setCloseMsg(e.target.value)}
                />
              </div>
              <p style={{ color: '#b91c1c', fontSize: '0.82rem', fontWeight: 600 }}>
                ⚠️ Once closed, the grievance lifecycle is formally completed and archived as read-only.
              </p>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ background: '#334155' }} disabled={modalLoading}>
                  {modalLoading ? 'Closing...' : 'Confirm Closure'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
