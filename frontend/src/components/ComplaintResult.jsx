import React, { useState } from 'react';
import { CheckCircle2, Building, ShieldAlert, Zap, AlertTriangle, ArrowRight, UserCheck, Cpu, ChevronDown, ChevronUp } from 'lucide-react';
import ConflictPanel from './ConflictPanel';

export default function ComplaintResult({ complaint, onReset }) {
  const [showTechnicalTrace, setShowTechnicalTrace] = useState(false);
  if (!complaint) return null;

  const getPriorityBadgeClass = (p) => {
    switch (p?.toUpperCase()) {
      case 'CRITICAL': return 'badge-critical';
      case 'HIGH': return 'badge-high';
      case 'MEDIUM': return 'badge-medium';
      default: return 'badge-low';
    }
  };

  const getEscalationBadgeClass = (e) => {
    switch (e?.toUpperCase()) {
      case 'IMMEDIATE': return 'badge-critical';
      case 'REQUIRED': return 'badge-high';
      default: return 'badge-neutral';
    }
  };

  return (
    <div>
      {/* Top Banner Outcome */}
      <div className="card" style={{ borderTop: '4px solid #1e3a8a' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
              Deterministic AI Disposition
            </span>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' }}>
              Complaint ID: {complaint.complaint_id}
            </h2>
            <p style={{ fontSize: '0.88rem', color: '#475569', marginTop: '0.2rem' }}>
              Filed by <strong>{complaint.citizen_name}</strong> for {complaint.ward}, {complaint.location}
            </p>
          </div>
          {onReset && (
            <button className="btn btn-secondary" onClick={onReset}>
              File Another Grievance
            </button>
          )}
        </div>

        {/* Core Decision Cards */}
        <div className="stats-grid">
          <div className="stat-box primary">
            <span className="stat-label">Assigned Department</span>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1e3a8a', display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.35rem' }}>
              <Building size={20} />
              {complaint.department || 'Unassigned (Manual Review)'}
            </div>
            {complaint.manual_override ? (
              <span style={{ fontSize: '0.75rem', color: '#b45309', fontWeight: 600, marginTop: '0.3rem' }}>
                * Manually Overridden (AI Suggested: {complaint.ai_department})
              </span>
            ) : (
              <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                Determined via Forward Chaining
              </span>
            )}
          </div>

          <div className={`stat-box ${complaint.priority?.toLowerCase()}`}>
            <span className="stat-label">Priority Level</span>
            <div style={{ marginTop: '0.35rem' }}>
              <span className={`badge ${getPriorityBadgeClass(complaint.priority)}`} style={{ fontSize: '0.9rem', padding: '0.35rem 0.8rem' }}>
                {complaint.priority}
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
              Arbitrated by precedence hierarchy
            </span>
          </div>

          <div className="stat-box">
            <span className="stat-label">Escalation Tier</span>
            <div style={{ marginTop: '0.35rem' }}>
              <span className={`badge ${getEscalationBadgeClass(complaint.escalation)}`} style={{ fontSize: '0.9rem', padding: '0.35rem 0.8rem' }}>
                <Zap size={14} />
                {complaint.escalation}
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
              Second-order rule evaluation
            </span>
          </div>

          <div className="stat-box">
            <span className="stat-label">Current Status</span>
            <div style={{ marginTop: '0.35rem' }}>
              <span className="badge badge-neutral" style={{ fontSize: '0.9rem', padding: '0.35rem 0.8rem' }}>
                {complaint.status}
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
              Evidence Cataloged: {complaint.evidence_available ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>

      {/* Conflicts & Contradictions Panel */}
      <ConflictPanel conflicts={complaint.conflicts} />

      {/* AI Decision Explanation Card */}
      <div className="card" style={{ marginTop: '1.5rem', border: '1px solid #93c5fd', background: '#ffffff' }}>
        <div className="card-header" style={{ borderBottomColor: '#bfdbfe', background: '#f0f7ff', borderRadius: '8px 8px 0 0' }}>
          <div>
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#1e3a8a' }}>
              <Cpu size={20} color="#2563eb" />
              AI Decision Explanation
            </h3>
            <p className="card-subtitle">
              Deterministic reasoning and explanation derived strictly from verified ground facts and fired rules.
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
    </div>
  );
}
