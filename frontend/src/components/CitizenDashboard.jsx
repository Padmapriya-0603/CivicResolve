import React, { useState, useEffect } from 'react';
import {
  Send,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Eye,
  RefreshCw,
  Building,
  ShieldCheck,
  GitBranch,
  ArrowRight,
  Bell,
  Check,
  Lock,
  Wrench,
  MessageSquare
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import GrievanceFlowchart from './GrievanceFlowchart';

export default function CitizenDashboard({ onNavigateSubmit, onSelectComplaint }) {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedFlowchartId, setSelectedFlowchartId] = useState(null);
  const [showNotifications, setShowNotifications] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [complaintList, notifRes] = await Promise.all([
        api.getComplaints(),
        api.getNotifications().catch(() => ({ notifications: [], unread_count: 0 }))
      ]);
      setComplaints(complaintList || []);
      setNotifications(notifRes.notifications || []);
      setUnreadCount(notifRes.unread_count || 0);

      if (complaintList && complaintList.length > 0) {
        setSelectedFlowchartId(prev => {
          if (prev && complaintList.some(c => c.complaint_id === prev)) return prev;
          const active = complaintList.find(c => !['CLOSED', 'Closed'].includes(c.status));
          return active ? active.complaint_id : complaintList[0].complaint_id;
        });
      }
    } catch (err) {
      console.error('Failed to load citizen data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleMarkRead = async (id) => {
    try {
      await api.markNotificationRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) {
      console.error('Failed to mark notification read', e);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (e) {
      console.error('Failed to mark all read', e);
    }
  };

  // Status mapping and counters
  const total = complaints.length;
  const submitted = complaints.filter(c => ['SUBMITTED', 'Submitted'].includes(c.status)).length;
  const acknowledged = complaints.filter(c => ['ACKNOWLEDGED', 'Acknowledged', 'Under Review', 'ACCEPTED', 'Accepted', 'Assigned'].includes(c.status)).length;
  const inProgress = complaints.filter(c => ['IN_PROGRESS', 'In Progress'].includes(c.status)).length;
  const resolved = complaints.filter(c => ['RESOLVED', 'Resolved', 'WORK_COMPLETED', 'Work Completed', 'USER_INFORMED', 'User Informed'].includes(c.status)).length;
  const closed = complaints.filter(c => ['CLOSED', 'Closed'].includes(c.status)).length;

  const activeFlowchartComp = complaints.find(c => c.complaint_id === selectedFlowchartId) || complaints[0];

  const getPriorityBadge = (p) => {
    switch (p?.toUpperCase()) {
      case 'CRITICAL': return <span className="badge badge-critical">CRITICAL</span>;
      case 'HIGH': return <span className="badge badge-high">HIGH</span>;
      case 'MEDIUM': return <span className="badge badge-medium">MEDIUM</span>;
      default: return <span className="badge badge-low">LOW</span>;
    }
  };

  const getStatusBadge = (status) => {
    const s = status?.toUpperCase().replace(' ', '_');
    switch (s) {
      case 'CLOSED':
        return <span className="badge badge-low" style={{ fontWeight: 700 }}>✓ Closed</span>;
      case 'RESOLVED':
      case 'USER_INFORMED':
      case 'WORK_COMPLETED':
        return <span className="badge" style={{ background: '#dcfce7', color: '#15803d', fontWeight: 700 }}>Resolved</span>;
      case 'IN_PROGRESS':
        return <span className="badge badge-high">Work in Progress</span>;
      case 'ACKNOWLEDGED':
      case 'ACCEPTED':
      case 'ASSIGNED':
      case 'UNDER_REVIEW':
        return <span className="badge" style={{ background: '#fef3c7', color: '#b45309', fontWeight: 600 }}>Acknowledged</span>;
      default:
        return <span className="badge badge-med">Submitted</span>;
    }
  };

  return (
    <div>
      {/* Welcome Banner with In-App Notifications Toggle */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #0f766e 0%, #115e59 100%)', color: '#ffffff', border: 'none' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.85 }}>
              Citizen Civic Services Portal
            </span>
            <h1 style={{ fontSize: '1.65rem', fontWeight: 800, marginTop: '0.2rem' }}>
              Welcome back, {user?.name || 'Citizen'}!
            </h1>
            <p style={{ fontSize: '0.88rem', opacity: 0.9, maxWidth: '650px', marginTop: '0.3rem' }}>
              Track the 5-stage progression of your grievances, inspect administrative response messages, and receive real-time resolution notices.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
            <button
              className="btn"
              style={{ backgroundColor: showNotifications ? '#ccfbf1' : 'rgba(255,255,255,0.2)', color: '#ffffff', border: '1px solid rgba(255,255,255,0.4)', position: 'relative' }}
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <Bell size={16} />
              Notifications
              {unreadCount > 0 && (
                <span style={{ background: '#ef4444', color: '#ffffff', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '10px', marginLeft: '0.3rem', fontWeight: 800 }}>
                  {unreadCount}
                </span>
              )}
            </button>

            <button
              className="btn"
              style={{ backgroundColor: '#ffffff', color: '#0f766e', fontWeight: 700 }}
              onClick={onNavigateSubmit}
            >
              <Send size={16} />
              Submit New Grievance
            </button>
          </div>
        </div>
      </div>

      {/* Notifications Drawer (Section 89) */}
      {showNotifications && (
        <div className="card" style={{ background: '#f8fafc', border: '1.5px solid #0f766e', marginBottom: '1.5rem', boxShadow: 'var(--shadow-md)' }}>
          <div className="card-header" style={{ borderBottomColor: '#cbd5e1' }}>
            <div>
              <h3 className="card-title" style={{ color: '#0f766e', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Bell size={18} color="#0f766e" />
                In-App Notifications ({notifications.length})
              </h3>
              <p className="card-subtitle">
                Official lifecycle events dispatched by municipal administrators and officers.
              </p>
            </div>
            {unreadCount > 0 && (
              <button className="btn btn-secondary" style={{ fontSize: '0.78rem', padding: '0.3rem 0.6rem' }} onClick={handleMarkAllRead}>
                Mark All as Read
              </button>
            )}
          </div>

          {notifications.length === 0 ? (
            <p style={{ color: '#64748b', fontSize: '0.85rem', textAlign: 'center', padding: '1.5rem' }}>
              No notifications currently on file.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '280px', overflowY: 'auto' }}>
              {notifications.map(n => (
                <div
                  key={n.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.75rem 1rem',
                    background: n.is_read ? '#ffffff' : '#f0fdfa',
                    border: `1px solid ${n.is_read ? '#e2e8f0' : '#99f6e4'}`,
                    borderLeft: `4px solid ${n.is_read ? '#cbd5e1' : '#0f766e'}`,
                    borderRadius: '6px'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#0f172a' }}>{n.title}</span>
                      <span className="badge" style={{ fontSize: '0.68rem', background: '#e2e8f0', color: '#475569' }}>
                        #{n.complaint_id}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: '#334155', margin: '0.2rem 0' }}>{n.message}</p>
                    <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{n.created_at}</span>
                  </div>

                  {!n.is_read && (
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.72rem', padding: '0.25rem 0.5rem' }}
                      onClick={() => handleMarkRead(n.id)}
                    >
                      <Check size={12} /> Read
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* KPI Cards */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <div className="stat-box primary">
          <span className="stat-label">Total Grievances</span>
          <div className="stat-value">{total}</div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Cumulative filed</span>
        </div>

        <div className="stat-box med">
          <span className="stat-label">1. Submitted</span>
          <div className="stat-value" style={{ color: '#b45309' }}>{submitted}</div>
          <span style={{ fontSize: '0.75rem', color: '#b45309' }}>Awaiting initial review</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #7c3aed', background: '#faf5ff' }}>
          <span className="stat-label" style={{ color: '#6d28d9' }}>2. Acknowledged</span>
          <div className="stat-value" style={{ color: '#7c3aed' }}>{acknowledged}</div>
          <span style={{ fontSize: '0.72rem', color: '#6d28d9' }}>Accepted &amp; Dispatched</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #2563eb', background: '#eff6ff' }}>
          <span className="stat-label" style={{ color: '#1e40af' }}>3. In Progress</span>
          <div className="stat-value" style={{ color: '#2563eb' }}>{inProgress}</div>
          <span style={{ fontSize: '0.72rem', color: '#1e40af' }}>Field work underway</span>
        </div>

        <div className="stat-box" style={{ borderLeft: '4px solid #0f766e', background: '#f0fdfa' }}>
          <span className="stat-label" style={{ color: '#0f766e' }}>4. Resolved</span>
          <div className="stat-value" style={{ color: '#0f766e' }}>{resolved}</div>
          <span style={{ fontSize: '0.72rem', color: '#0f766e' }}>Work done &amp; notified</span>
        </div>

        <div className="stat-box low">
          <span className="stat-label">5. Closed</span>
          <div className="stat-value" style={{ color: '#15803d' }}>{closed}</div>
          <span style={{ fontSize: '0.72rem', color: '#15803d' }}>Lifecycle completed</span>
        </div>
      </div>

      {/* ============================================================== */}
      {/* 5-STAGE DYNAMIC PROGRESS METER & FLOWCHART */}
      {/* ============================================================== */}
      {complaints.length > 0 && activeFlowchartComp && (
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: 0, display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <GitBranch size={18} color="#0f766e" />
              Active Grievance Progress Meter
            </h2>

            {complaints.length > 1 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 700, color: '#334155' }}>Select Grievance:</label>
                <select
                  className="form-select"
                  style={{ width: 'auto', padding: '0.3rem 0.65rem', fontSize: '0.82rem', fontWeight: 600 }}
                  value={activeFlowchartComp.complaint_id}
                  onChange={(e) => setSelectedFlowchartId(e.target.value)}
                >
                  {complaints.map(c => (
                    <option key={c.complaint_id} value={c.complaint_id}>
                      #{c.complaint_id} — {c.issue_type} ({c.status_display || c.status})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <GrievanceFlowchart complaint={activeFlowchartComp} />
        </div>
      )}

      {/* My Complaints List */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <FileText size={18} />
              My Registered Grievances ({total})
            </h2>
            <p className="card-subtitle">
              Live status tracking of all complaints submitted under your citizen profile.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            Refresh
          </button>
        </div>

        {complaints.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
            <p style={{ marginBottom: '1rem' }}>You have not submitted any grievances yet.</p>
            <button className="btn btn-primary" onClick={onNavigateSubmit}>
              Submit Your First Grievance
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket ID</th>
                  <th>Submitted Date</th>
                  <th>Category &amp; Issue</th>
                  <th>Department</th>
                  <th>Priority</th>
                  <th>Current Stage</th>
                  <th>Progress</th>
                  <th>Latest Official Update</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {complaints.map((c) => {
                  const percent = c.progress_percent || 14;
                  const stageNum = c.current_stage_number || 1;
                  return (
                    <tr key={c.complaint_id}>
                      <td><strong>{c.complaint_id}</strong></td>
                      <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        {c.created_at ? c.created_at.split(' ')[0] : 'Today'}
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{c.issue_type}</div>
                        <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{c.category} &bull; {c.ward}</div>
                      </td>
                      <td>
                        <span style={{ fontWeight: 600, color: c.department ? '#0f766e' : '#b45309' }}>
                          {c.department || 'Pending Assignment'}
                        </span>
                      </td>
                      <td>{getPriorityBadge(c.priority)}</td>
                      <td>{getStatusBadge(c.status)}</td>
                      <td style={{ minWidth: '120px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', fontWeight: 700, marginBottom: '0.2rem' }}>
                          <span>Stage {stageNum}/7</span>
                          <span>{percent}%</span>
                        </div>
                        <div style={{ width: '100%', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${percent}%`, height: '100%', background: percent === 100 ? '#16a34a' : '#0f766e', borderRadius: '3px' }} />
                        </div>
                      </td>
                      <td style={{ maxWidth: '200px' }}>
                        {c.notification_message ? (
                          <div style={{ fontSize: '0.75rem', color: '#166534', background: '#dcfce7', padding: '0.2rem 0.45rem', borderRadius: '4px' }} title={c.notification_message}>
                            <strong>Resolved:</strong> {c.notification_message.length > 35 ? `${c.notification_message.substring(0, 35)}...` : c.notification_message}
                          </div>
                        ) : c.completion_message ? (
                          <div style={{ fontSize: '0.75rem', color: '#1e40af', background: '#dbeafe', padding: '0.2rem 0.45rem', borderRadius: '4px' }} title={c.completion_message}>
                            <strong>Work Done:</strong> {c.completion_message.length > 35 ? `${c.completion_message.substring(0, 35)}...` : c.completion_message}
                          </div>
                        ) : c.admin_message ? (
                          <div style={{ fontSize: '0.75rem', color: '#0f766e', background: '#ccfbf1', padding: '0.2rem 0.45rem', borderRadius: '4px' }} title={c.admin_message}>
                            <strong>Accepted:</strong> {c.admin_message.length > 35 ? `${c.admin_message.substring(0, 35)}...` : c.admin_message}
                          </div>
                        ) : (
                          <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontStyle: 'italic' }}>
                            Awaiting admin review
                          </span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.35rem' }}>
                          <button
                            className="btn btn-secondary"
                            style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem', color: '#0f766e' }}
                            title="Show flowchart for this ticket"
                            onClick={() => {
                              setSelectedFlowchartId(c.complaint_id);
                              window.scrollTo({ top: 220, behavior: 'smooth' });
                            }}
                          >
                            <GitBranch size={13} />
                          </button>
                          <button
                            className="btn btn-secondary"
                            style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem' }}
                            onClick={() => onSelectComplaint(c.complaint_id)}
                          >
                            <Eye size={13} /> View
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
