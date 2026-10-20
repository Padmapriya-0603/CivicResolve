import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Building,
  User,
  History,
  Send,
  Wrench,
  Eye,
  Check,
  Lock,
  PlusCircle,
  MessageSquare,
  ShieldCheck,
  Calendar,
  MapPin,
  Tag,
  FileText,
  CheckCircle,
  AlertCircle,
  Paperclip,
  Image as ImageIcon,
  ExternalLink,
  Download,
  Cpu,
  GitCommit,
  Code
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import GrievanceFlowchart from './GrievanceFlowchart';

const isImageFile = (filename) => {
  if (!filename) return false;
  const ext = filename.toLowerCase().split('.').pop();
  return ['png', 'jpg', 'jpeg', 'webp'].includes(ext);
};

const isPdfFile = (filename) => {
  if (!filename) return false;
  return filename.toLowerCase().endsWith('.pdf');
};

export default function ComplaintDetails({ complaintId, onBack }) {
  const { user } = useAuth();
  const [complaint, setComplaint] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states for each lifecycle step
  const [actionLoading, setActionLoading] = useState(false);
  const [activeModal, setActiveModal] = useState(null); // 'ACK', 'ACCEPT', 'START_WORK', 'PROGRESS_UPDATE', 'COMPLETE', 'INFORM', 'CLOSE'

  // Input fields
  const [ackNotes, setAckNotes] = useState('');
  const [acceptDept, setAcceptDept] = useState('');
  const [acceptPriority, setAcceptPriority] = useState('MEDIUM');
  const [acceptMessage, setAcceptMessage] = useState('');
  const [startWorkMessage, setStartWorkMessage] = useState('');
  const [progressUpdateMessage, setProgressUpdateMessage] = useState('');
  const [completionMessage, setCompletionMessage] = useState('');
  const [informMessage, setInformMessage] = useState('');
  const [closureMessage, setClosureMessage] = useState('');
  const [showAiAudit, setShowAiAudit] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      let comp = null;
      let depts = [];
      try {
        comp = await api.getComplaintById(complaintId);
      } catch (cErr) {
        console.error('Failed to get complaint by id', cErr);
      }

      try {
        depts = await api.getDepartments();
      } catch (dErr) {
        console.warn('Could not load departments list', dErr);
        depts = [];
      }

      if (comp) {
        setComplaint(comp);
        setDepartments(depts || []);
        if (comp.department) {
          setAcceptDept(comp.department);
        } else if (depts && depts.length > 0) {
          setAcceptDept(depts[0].name);
        }
        setAcceptPriority(comp.priority || 'MEDIUM');
        setAcceptMessage(`Your grievance #${comp.complaint_id} has been accepted by Municipal Administration and dispatched for resolution.`);
        setInformMessage(`Your grievance #${comp.complaint_id} has been successfully resolved and verified.`);
      } else {
        setComplaint(null);
      }
    } catch (err) {
      console.error('Failed to load complaint details', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [complaintId]);

  if (loading) {
    return <div className="card"><p>Loading complaint details...</p></div>;
  }

  if (!complaint) {
    return (
      <div className="card">
        <p>Complaint not found.</p>
        <button className="btn btn-secondary" onClick={onBack}>Go Back</button>
      </div>
    );
  }

  const isAdmin = user?.role === 'ADMIN';
  const isOfficer = user?.role === 'DEPARTMENT_OFFICER';
  const isCitizen = user?.role === 'CITIZEN';
  const status = complaint.status?.toUpperCase().replace(' ', '_');

  // Lifecycle Action Handlers (Sections 74 - 81)
  const handleAcknowledge = async () => {
    setActionLoading(true);
    try {
      const updated = await api.acknowledgeComplaint(complaintId, ackNotes || undefined);
      setComplaint(updated);
      setActiveModal(null);
      alert('Complaint acknowledged successfully.');
    } catch (err) {
      alert(`Acknowledgement failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAccept = async (e) => {
    e.preventDefault();
    if (!acceptMessage.trim()) {
      alert('Acceptance response message to citizen is required.');
      return;
    }
    setActionLoading(true);
    try {
      const updated = await api.acceptComplaint(complaintId, {
        department: acceptDept,
        priority: acceptPriority,
        message: acceptMessage.trim()
      });
      setComplaint(updated);
      setActiveModal(null);
      alert('Complaint accepted and response message transmitted to citizen.');
    } catch (err) {
      alert(`Acceptance failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartWork = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      const updated = await api.startWork(complaintId, startWorkMessage || undefined);
      setComplaint(updated);
      setActiveModal(null);
      alert('Work started and citizen notified.');
    } catch (err) {
      alert(`Start work failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddProgressUpdate = async (e) => {
    e.preventDefault();
    if (!progressUpdateMessage.trim()) {
      alert('Please enter a progress update message.');
      return;
    }
    setActionLoading(true);
    try {
      const updated = await api.addProgressUpdate(complaintId, progressUpdateMessage.trim());
      setComplaint(updated);
      setProgressUpdateMessage('');
      setActiveModal(null);
      alert('Progress update published and transmitted to citizen.');
    } catch (err) {
      alert(`Progress update failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteWork = async (e) => {
    e.preventDefault();
    if (!completionMessage.trim()) {
      alert('Please enter a work completion description.');
      return;
    }
    setActionLoading(true);
    try {
      const updated = await api.completeWork(complaintId, completionMessage.trim());
      setComplaint(updated);
      setActiveModal(null);
      alert('Work marked completed. Next step: Inform citizen of resolution.');
    } catch (err) {
      alert(`Completion update failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleInformUser = async (e) => {
    e.preventDefault();
    if (!informMessage.trim()) {
      alert('Please enter the resolution notification message for the citizen.');
      return;
    }
    setActionLoading(true);
    try {
      const updated = await api.informUser(complaintId, informMessage.trim());
      setComplaint(updated);
      setActiveModal(null);
      alert('Citizen officially informed of resolution. Ticket can now be closed.');
    } catch (err) {
      alert(`Notification failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloseComplaint = async () => {
    if (!window.confirm('Are you sure you want to formally close this complaint? Once closed, it becomes read-only.')) {
      return;
    }
    setActionLoading(true);
    try {
      const updated = await api.closeComplaint(complaintId, closureMessage || undefined);
      setComplaint(updated);
      setActiveModal(null);
      alert('Complaint lifecycle formally closed.');
    } catch (err) {
      alert(`Closure failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div>
      {/* Navigation Top */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <button className="btn btn-secondary" onClick={onBack}>
          <ArrowLeft size={16} />
          Back to Grievances
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="badge badge-primary">ID: {complaint.complaint_id}</span>
          <span
            className="badge"
            style={{
              background: status === 'CLOSED' ? '#15803d' : (status === 'USER_INFORMED' ? '#0f766e' : '#2563eb'),
              color: '#ffffff',
              fontSize: '0.85rem'
            }}
          >
            {complaint.status_display || complaint.status}
          </span>
        </div>
      </div>

      {/* 5-STAGE DYNAMIC PROGRESS METER */}
      <GrievanceFlowchart complaint={complaint} />

      {/* ============================================================== */}
      {/* ADMIN & OFFICER ACTION CONSOLE (Section 86) */}
      {/* ============================================================== */}
      {(isAdmin || isOfficer) && (
        <div className="card" style={{ background: '#f8fafc', border: '2px solid #0f766e', marginBottom: '1.5rem', boxShadow: 'var(--shadow-md)' }}>
          <div className="card-header" style={{ borderBottomColor: '#cbd5e1' }}>
            <div>
              <h3 className="card-title" style={{ color: '#0f766e', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                <ShieldCheck size={18} color="#0f766e" />
                Administrative Lifecycle Action Console
              </h3>
              <p className="card-subtitle">
                Current Operational State: <strong>{complaint.status_display || complaint.status}</strong>. Buttons correspond to allowed transitions.
              </p>
            </div>
            <span className="badge badge-med">Stage {complaint.current_stage_number || 1} of 5</span>
          </div>

          <div style={{ padding: '0.5rem 0' }}>
            {/* STAGE 1: SUBMITTED -> Show [ACKNOWLEDGE] for Admin */}
            {status === 'SUBMITTED' && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h4 style={{ margin: 0, color: '#0f172a', fontSize: '0.95rem' }}>Step 1: Acknowledge Receipt</h4>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.82rem', color: '#64748b' }}>
                    {isAdmin
                      ? <>Confirm receipt of this citizen grievance to advance to <strong>ACKNOWLEDGED</strong>.</>
                      : <>Grievance logged. Pending Municipal Administrator review and formal acknowledgement.</>}
                  </p>
                </div>
                {isAdmin ? (
                  <button
                    className="btn btn-primary"
                    style={{ background: '#0f766e', borderColor: '#0f766e', fontWeight: 700 }}
                    onClick={() => setActiveModal('ACK')}
                  >
                    <Check size={16} /> Acknowledge Complaint
                  </button>
                ) : (
                  <span className="badge badge-med">Pending Admin Acknowledgment</span>
                )}
              </div>
            )}

            {/* STAGE 2: ACKNOWLEDGED / ACCEPTED -> Department Officer starts work */}
            {(status === 'ACKNOWLEDGED' || status === 'ACCEPTED') && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h4 style={{ margin: 0, color: '#0f172a', fontSize: '0.95rem' }}>Step 2: Department Work Dispatch</h4>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.82rem', color: '#64748b' }}>
                    {isOfficer
                      ? <>Review assigned field ticket and click <strong>Start Work</strong> to begin remediation (advances to <strong>IN_PROGRESS</strong>).</>
                      : <>Acknowledged and routed to <strong>{complaint.department || 'Assigned Department'}</strong>. Awaiting Department Officer to accept and start work.</>}
                  </p>
                </div>
                {isOfficer ? (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-primary"
                      style={{ background: '#2563eb', borderColor: '#2563eb', fontWeight: 700 }}
                      onClick={() => setActiveModal('START_WORK')}
                    >
                      <Wrench size={16} /> Start Work
                    </button>
                  </div>
                ) : (
                  <span className="badge badge-med" style={{ background: '#eff6ff', color: '#1d4ed8', border: '1px solid #bfdbfe', fontWeight: 600 }}>
                    ⏳ Awaiting Department Officer to Start Work
                  </span>
                )}
              </div>
            )}

            {/* STAGE 3: IN_PROGRESS -> Department Officer adds updates & resolves */}
            {status === 'IN_PROGRESS' && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h4 style={{ margin: 0, color: '#0f172a', fontSize: '0.95rem' }}>Step 3: Field Operations &amp; Resolution</h4>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.82rem', color: '#64748b' }}>
                    {isOfficer
                      ? <>Post live field updates or click <strong>Mark Resolved</strong> once repairs/remediation are complete.</>
                      : <>Field crew from <strong>{complaint.department || 'Department'}</strong> is currently executing work. Awaiting Officer resolution report.</>}
                  </p>
                </div>
                {isOfficer ? (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ fontWeight: 600 }}
                      onClick={() => setActiveModal('PROGRESS_UPDATE')}
                    >
                      <PlusCircle size={15} /> Add Progress Update
                    </button>
                    <button
                      className="btn btn-primary"
                      style={{ background: '#16a34a', borderColor: '#16a34a', fontWeight: 700 }}
                      onClick={() => setActiveModal('COMPLETE')}
                    >
                      <CheckCircle2 size={16} /> Mark Resolved
                    </button>
                  </div>
                ) : (
                  <span className="badge badge-low" style={{ background: '#f0f9ff', color: '#0369a1', border: '1px solid #bae6fd', fontWeight: 600 }}>
                    🔧 Field Work Underway (Officer Active)
                  </span>
                )}
              </div>
            )}

            {/* STAGE 4: RESOLVED / WORK_COMPLETED / USER_INFORMED -> Admin Verifies and Closes */}
            {['WORK_COMPLETED', 'USER_INFORMED', 'RESOLVED'].includes(status) && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h4 style={{ margin: 0, color: '#0f172a', fontSize: '0.95rem' }}>Step 4: Verification &amp; Formal Closure</h4>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.82rem', color: '#64748b' }}>
                    {isAdmin
                      ? 'Work has been completed and marked resolved by the Department Officer. Verify field remediation and formally close ticket.'
                      : 'Field work completed and marked resolved. Waiting for Municipal Administrator verification and formal closure.'}
                  </p>
                </div>
                {isAdmin ? (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-primary"
                      style={{ background: '#334155', borderColor: '#334155', fontWeight: 700 }}
                      onClick={() => setActiveModal('CLOSE')}
                    >
                      <Lock size={16} /> Verify &amp; Close Complaint
                    </button>
                  </div>
                ) : (
                  <span className="badge badge-low" style={{ background: '#dcfce7', color: '#15803d', fontWeight: 700, padding: '0.4rem 0.75rem', border: '1px solid #86efac' }}>
                    ✓ Work Resolved &bull; Pending Admin Closure
                  </span>
                )}
              </div>
            )}

            {/* STAGE 5: CLOSED -> Read-only message */}
            {status === 'CLOSED' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#166534', fontWeight: 700 }}>
                <CheckCircle2 size={20} color="#16a34a" />
                This complaint lifecycle is formally CLOSED. Ticket is archived as read-only.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* ACTION MODALS FOR THE 5 STAGES */}
      {/* ============================================================== */}

      {/* Modal: Acknowledge */}
      {activeModal === 'ACK' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Acknowledge Complaint #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <p style={{ fontSize: '0.88rem', color: '#475569' }}>
                Acknowledging this complaint confirms receipt by municipal administration and advances it to stage 2.
              </p>
              <div className="form-group">
                <label className="form-label">Acknowledgement Notes (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Complaint received and logged into municipal queue."
                  value={ackNotes}
                  onChange={(e) => setAckNotes(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button className="btn btn-primary" onClick={handleAcknowledge} disabled={actionLoading}>
                  {actionLoading ? 'Acknowledging...' : 'Confirm Acknowledgement'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Accept Complaint */}
      {activeModal === 'ACCEPT' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '560px', maxWidth: '92%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Accept Grievance #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleAccept} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Responsible Department *</label>
                  <select
                    className="form-select"
                    value={acceptDept}
                    onChange={(e) => setAcceptDept(e.target.value)}
                    required
                  >
                    {departments.map((d) => (
                      <option key={d.department_id} value={d.name}>{d.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Priority Level *</label>
                  <select
                    className="form-select"
                    value={acceptPriority}
                    onChange={(e) => setAcceptPriority(e.target.value)}
                    required
                  >
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
                  value={acceptMessage}
                  onChange={(e) => setAcceptMessage(e.target.value)}
                  placeholder="e.g. Your complaint has been reviewed and accepted. The concerned department has been instructed to take necessary action."
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={actionLoading}>
                  {actionLoading ? 'Accepting...' : 'Accept Complaint & Inform Citizen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Start Work */}
      {activeModal === 'START_WORK' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Start Work: #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleStartWork} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Work Started Description (Sent to Citizen)</label>
                <textarea
                  className="form-input"
                  rows="2"
                  value={startWorkMessage}
                  onChange={(e) => setStartWorkMessage(e.target.value)}
                  placeholder="e.g. The maintenance team has been assigned and inspection has started."
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={actionLoading}>
                  {actionLoading ? 'Starting Work...' : 'Confirm Work Started'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Progress Update */}
      {activeModal === 'PROGRESS_UPDATE' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Add Progress Update: #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleAddProgressUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Progress Update Message *</label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={progressUpdateMessage}
                  onChange={(e) => setProgressUpdateMessage(e.target.value)}
                  placeholder="e.g. Inspection completed. Replacement of the damaged component is underway."
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={actionLoading}>
                  {actionLoading ? 'Publishing...' : 'Publish Update to Citizen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Complete Work */}
      {activeModal === 'COMPLETE' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '540px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Mark Work Completed: #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleCompleteWork} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div className="form-group">
                <label className="form-label">Work Completion Description *</label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={completionMessage}
                  onChange={(e) => setCompletionMessage(e.target.value)}
                  placeholder="e.g. The damaged streetlight component has been replaced and the streetlight is functioning normally."
                  required
                />
                <small style={{ color: '#64748b', display: 'block', marginTop: '0.25rem' }}>
                  Note: Marking work completed advances the state to WORK_COMPLETED. In the next step, you will explicitly inform the citizen.
                </small>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={actionLoading}>
                  {actionLoading ? 'Saving...' : 'Confirm Work Completed'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Inform User */}
      {activeModal === 'INFORM' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '540px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Inform Citizen of Resolution: #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <form onSubmit={handleInformUser} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              {complaint.completion_message && (
                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.82rem' }}>
                  <strong>Field Completion Report:</strong> {complaint.completion_message}
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Final Resolution Notice to Citizen *</label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={informMessage}
                  onChange={(e) => setInformMessage(e.target.value)}
                  placeholder="e.g. Your complaint has been resolved. The damaged streetlight has been repaired and is now functioning normally."
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={actionLoading}>
                  {actionLoading ? 'Informing...' : 'Send Resolution Notice to Citizen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Close Complaint */}
      {activeModal === 'CLOSE' && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '540px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <h3 className="card-title">Close Grievance #{complaint.complaint_id}</h3>
              <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>✕</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
              <div style={{ background: '#f0fdf4', padding: '0.85rem', borderRadius: '6px', border: '1px solid #bbf7d0', fontSize: '0.85rem' }}>
                <p><strong>Field Completion:</strong> {complaint.completion_message || 'Completed'}</p>
                <p style={{ marginTop: '0.25rem' }}><strong>Final Response to Citizen:</strong> {complaint.notification_message || complaint.resolution_message || 'Informed'}</p>
              </div>
              <div className="form-group">
                <label className="form-label">Closure Summary Notes (Optional)</label>
                <textarea
                  className="form-input"
                  rows="2"
                  value={closureMessage}
                  onChange={(e) => setClosureMessage(e.target.value)}
                  placeholder="e.g. Work inspected and verified. All SLA criteria satisfied."
                />
              </div>
              <p style={{ color: '#b91c1c', fontSize: '0.82rem', fontWeight: 600 }}>
                ⚠️ Are you sure you want to close this complaint? Once closed, it becomes read-only.
              </p>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button className="btn btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button className="btn btn-primary" style={{ background: '#0f172a' }} onClick={handleCloseComplaint} disabled={actionLoading}>
                  {actionLoading ? 'Closing...' : 'Confirm & Formally Close Ticket'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* ADMINISTRATION UPDATES & TIMELINE (Section 84 & 88) */}
      {/* ============================================================== */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <History size={18} color="#1e3a8a" />
              Administration Updates &amp; Chronological Timeline
            </h3>
            <p className="card-subtitle">
              Auditable, timestamped record of every stage transition, progress update, and communication.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', padding: '0.5rem 0' }}>
          {complaint.timeline && complaint.timeline.length > 0 ? (
            complaint.timeline.map((tm, idx) => (
              <div
                key={tm.id || idx}
                style={{
                  display: 'flex',
                  gap: '1rem',
                  padding: '1rem',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  borderLeft: `4px solid ${
                    tm.status === 'CLOSED' ? '#16a34a' :
                    (tm.status === 'USER_INFORMED' ? '#0f766e' :
                    (tm.status === 'WORK_COMPLETED' ? '#2563eb' :
                    (tm.status === 'IN_PROGRESS' ? '#3b82f6' :
                    (tm.status === 'ACCEPTED' ? '#7c3aed' :
                    (tm.status === 'ACKNOWLEDGED' ? '#d97706' : '#64748b')))))
                  }`
                }}
              >
                <div style={{ marginTop: '0.2rem' }}>
                  {tm.status === 'CLOSED' ? <Lock size={18} color="#16a34a" /> :
                   tm.status === 'USER_INFORMED' ? <Send size={18} color="#0f766e" /> :
                   tm.status === 'WORK_COMPLETED' ? <CheckCircle2 size={18} color="#2563eb" /> :
                   tm.status === 'IN_PROGRESS' ? <Wrench size={18} color="#3b82f6" /> :
                   tm.status === 'ACCEPTED' ? <ShieldCheck size={18} color="#7c3aed" /> :
                   tm.status === 'ACKNOWLEDGED' ? <Eye size={18} color="#d97706" /> :
                   <FileText size={18} color="#64748b" />}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a' }}>
                      {tm.status}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {tm.created_at}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.78rem', color: '#64748b', margin: '0.15rem 0' }}>
                    Action by: <strong>{tm.action_by}</strong> ({tm.action_by_role})
                  </div>

                  <p style={{ fontSize: '0.88rem', color: '#1e293b', marginTop: '0.4rem', background: '#ffffff', padding: '0.65rem 0.85rem', borderRadius: '6px', border: '1px solid #e2e8f0', lineHeight: 1.45 }}>
                    "{tm.message}"
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p style={{ color: '#64748b', fontSize: '0.85rem' }}>No timeline records available.</p>
          )}
        </div>
      </div>



      {/* ============================================================== */}
      {/* AI DECISION EXPLANATION */}
      {/* ============================================================== */}
      <div className="card" style={{ marginBottom: '1.5rem', border: '1px solid #93c5fd', background: '#ffffff' }}>
        <div className="card-header" style={{ borderBottomColor: '#bfdbfe', background: '#f0f7ff', borderRadius: '8px 8px 0 0' }}>
          <div>
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#1e3a8a' }}>
              <Cpu size={20} color="#2563eb" />
              AI Explanation
            </h3>
            <p className="card-subtitle">
              Deterministic reasoning and explanation provided by the AI grievance engine.
            </p>
          </div>
        </div>

        <div style={{ padding: '1.25rem' }}>
          {complaint.explanation ? (
            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.9rem', color: '#1e293b', lineHeight: '1.7' }}>
                {complaint.explanation}
              </pre>
            </div>
          ) : (
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', color: '#64748b', fontStyle: 'italic' }}>
              No AI explanation available for this complaint.
            </div>
          )}
        </div>
      </div>

      {/* SUPPORTING EVIDENCE / ATTACHMENT CARD (Visible to Citizen, Officer, and Admin) */}
      <div className="card" style={{ marginBottom: '1.5rem', border: complaint.evidence_filename ? '2px solid #2563eb' : '1px solid #cbd5e1' }}>
        <div className="card-header" style={{ borderBottomColor: '#e2e8f0' }}>
          <div>
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#1e3a8a' }}>
              <Paperclip size={18} color="#2563eb" />
              Supporting Evidence &amp; Field Documentation
            </h3>
            <p className="card-subtitle">
              Citizen-provided photo or PDF documentation for field inspection by Department Officers and Municipal Administrators.
            </p>
          </div>
          {complaint.evidence_filename && (
            <span className="badge badge-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              {isPdfFile(complaint.evidence_filename) ? <FileText size={13} /> : <ImageIcon size={13} />}
              {isPdfFile(complaint.evidence_filename) ? 'PDF Document' : 'Photo Attached'}
            </span>
          )}
        </div>

        {complaint.evidence_filename ? (
          <div>
            {isImageFile(complaint.evidence_filename) ? (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.88rem', fontWeight: 600, color: '#1e293b' }}>
                    <ImageIcon size={16} color="#2563eb" />
                    <span>Filename: <code>{complaint.evidence_filename}</code></span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <a
                      href={api.getEvidenceUrl(complaint.evidence_filename)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary"
                      style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                    >
                      <ExternalLink size={14} /> View Full Image
                    </a>
                    <a
                      href={api.getEvidenceUrl(complaint.evidence_filename)}
                      download={complaint.evidence_filename}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                    >
                      <Download size={14} /> Download
                    </a>
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                  <img
                    src={api.getEvidenceUrl(complaint.evidence_filename)}
                    alt="Citizen Uploaded Evidence"
                    style={{
                      maxWidth: '100%',
                      maxHeight: '450px',
                      borderRadius: '8px',
                      objectFit: 'contain',
                      boxShadow: '0 4px 14px rgba(0,0,0,0.08)',
                      cursor: 'pointer',
                      border: '1px solid #e2e8f0'
                    }}
                    onClick={() => window.open(api.getEvidenceUrl(complaint.evidence_filename), '_blank')}
                    title="Click to view high-resolution photo in new tab"
                  />
                  <p style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.6rem', marginBottom: 0 }}>
                    * Photographic evidence captured by citizen. Verified and preserved in municipal grievance registry.
                  </p>
                </div>
              </div>
            ) : isPdfFile(complaint.evidence_filename) ? (
              <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <div style={{ padding: '0.75rem', background: '#fee2e2', borderRadius: '10px', color: '#dc2626', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <FileText size={32} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '0.95rem' }}>
                        {complaint.evidence_filename}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.15rem' }}>
                        Official Citizen PDF Documentation &bull; Click to open in browser reader
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <a
                      href={api.getEvidenceUrl(complaint.evidence_filename)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary"
                      style={{ fontSize: '0.82rem', padding: '0.45rem 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: '#dc2626', borderColor: '#dc2626' }}
                    >
                      <ExternalLink size={15} /> Open PDF Document
                    </a>
                    <a
                      href={api.getEvidenceUrl(complaint.evidence_filename)}
                      download={complaint.evidence_filename}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.82rem', padding: '0.45rem 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                      <Download size={15} /> Download PDF
                    </a>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Paperclip size={18} color="#2563eb" />
                  <span>Attached File: <strong>{complaint.evidence_filename}</strong></span>
                </div>
                <a
                  href={api.getEvidenceUrl(complaint.evidence_filename)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  <ExternalLink size={14} /> Open File
                </a>
              </div>
            )}
          </div>
        ) : (
          <div style={{ padding: '0.5rem 0', color: '#64748b', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>No supporting photo or PDF documentation was attached to this grievance.</span>
          </div>
        )}
      </div>

      {/* COMPLAINT INFORMATION & PARTICULARS (Section 84) */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <User size={18} color="#1e3a8a" />
              Grievance Particulars &amp; Citizen Information
            </h3>
            <p className="card-subtitle">
              Structured parameters registered for ticket #{complaint.complaint_id}.
            </p>
          </div>
        </div>

        <div className="form-grid" style={{ marginBottom: '1rem' }}>
          <div>
            <span className="stat-label">Citizen Name</span>
            <p style={{ fontWeight: 600 }}>{complaint.citizen_name}</p>
          </div>
          <div>
            <span className="stat-label">Phone &amp; Email</span>
            <p style={{ fontWeight: 600 }}>{complaint.phone} / {complaint.email}</p>
          </div>
          <div>
            <span className="stat-label">Category &amp; Issue</span>
            <p style={{ fontWeight: 600 }}>{complaint.category} &rarr; {complaint.issue_type}</p>
          </div>
          <div>
            <span className="stat-label">Assigned Department</span>
            <p style={{ fontWeight: 600, color: '#0f766e' }}>
              {complaint.department || 'Awaiting assignment'}
              {complaint.admin_department_id && (
                <span style={{ marginLeft: '0.4rem', color: '#b45309', fontSize: '0.78rem', fontWeight: 500 }}>
                  (Admin Override)
                </span>
              )}
            </p>
          </div>
          <div>
            <span className="stat-label">Priority &amp; Escalation</span>
            <p style={{ fontWeight: 600 }}>{complaint.priority} ({complaint.escalation})</p>
          </div>
          <div>
            <span className="stat-label">Municipal Zone &amp; Ward (GCC)</span>
            <p style={{ fontWeight: 600 }}>
              {complaint.zone ? `${complaint.zone} • ` : ''}{complaint.ward}
            </p>
          </div>
          <div>
            <span className="stat-label">Landmark / Street</span>
            <p style={{ fontWeight: 600 }}>{complaint.location}</p>
          </div>
          <div>
            <span className="stat-label">Location Type</span>
            <p style={{ fontWeight: 600 }}>{complaint.location_type || 'Public Road'}</p>
          </div>
          <div>
            <span className="stat-label">Immediate Danger</span>
            <p style={{ fontWeight: 600, color: complaint.immediate_danger === 'YES' ? '#dc2626' : 'inherit' }}>
              {complaint.immediate_danger || (complaint.emergency ? 'YES' : 'NO')}
            </p>
          </div>
          <div>
            <span className="stat-label">Submission Date</span>
            <p style={{ fontWeight: 600 }}>{complaint.created_at}</p>
          </div>
          <div>
            <span className="stat-label">Current Stage</span>
            <p style={{ fontWeight: 700, color: '#1e3a8a' }}>{complaint.status_display || complaint.status} (Stage {complaint.current_stage_number || 1}/5)</p>
          </div>
        </div>

        {complaint.description && (
          <div style={{ background: '#f8fafc', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginTop: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase' }}>Citizen Grievance Description:</span>
            <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.88rem', color: '#1e293b' }}>
              "{complaint.description}"
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
