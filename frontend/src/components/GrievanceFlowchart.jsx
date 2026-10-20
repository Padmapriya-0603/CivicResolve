import React from 'react';
import {
  FileText,
  Eye,
  CheckCircle2,
  Wrench,
  Send,
  Lock,
  Clock,
  ShieldCheck,
  ArrowRight,
  AlertCircle
} from 'lucide-react';

const STAGES = [
  { key: 'SUBMITTED', step: 1, label: 'Submitted', percent: 20, icon: FileText, desc: 'Complaint submitted by citizen' },
  { key: 'ACKNOWLEDGED', step: 2, label: 'Acknowledged', percent: 40, icon: Eye, desc: 'Administration received and assigned' },
  { key: 'IN_PROGRESS', step: 3, label: 'In Progress', percent: 60, icon: Wrench, desc: 'Field work currently underway' },
  { key: 'RESOLVED', step: 4, label: 'Resolved', percent: 80, icon: CheckCircle2, desc: 'Work completed and resolution documented' },
  { key: 'CLOSED', step: 5, label: 'Closed', percent: 100, icon: Lock, desc: 'Complaint lifecycle closed' }
];

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

export default function GrievanceFlowchart({ complaint }) {
  if (!complaint) return null;

  const currentStatus = NORMALIZE[complaint.status] || 'SUBMITTED';
  const currentStageIndex = STAGES.findIndex(s => s.key === currentStatus);
  const activeIndex = currentStageIndex >= 0 ? currentStageIndex : 0;
  const currentStage = STAGES[activeIndex];
  const progressPercent = currentStage.percent;

  return (
    <div className="card" style={{ background: '#f8fafc', border: '1.5px solid #cbd5e1', marginBottom: '1.5rem', padding: '1.25rem' }}>
      {/* Header with Ticket ID, Stage X of 5, and Percentage */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#1e3a8a', display: 'flex', alignItems: 'center', gap: '0.45rem', margin: 0 }}>
            <ShieldCheck size={20} color="#1e3a8a" />
            5-Stage Grievance Lifecycle: Ticket #{complaint.complaint_id}
          </h3>
          <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '0.2rem 0 0 0' }}>
            Sequential tracking: Submitted &rarr; Acknowledged &rarr; In Progress &rarr; Resolved &rarr; Closed.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#0f766e' }}>
              Stage {currentStage.step} of 5 ({progressPercent}%)
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
              {currentStage.label}
            </div>
          </div>
          <span
            className="badge"
            style={{
              background: activeIndex === 4 ? '#15803d' : (activeIndex >= 2 ? '#0f766e' : '#2563eb'),
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '0.8rem',
              padding: '0.35rem 0.65rem'
            }}
          >
            {complaint.status_display || currentStage.label}
          </span>
        </div>
      </div>

      {/* Progress Bar Line */}
      <div style={{ width: '100%', height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginBottom: '1.25rem' }}>
        <div
          style={{
            width: `${progressPercent}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #0f766e 0%, #16a34a 100%)',
            transition: 'width 0.4s ease',
            borderRadius: '4px'
          }}
        />
      </div>

      {/* Horizontal / Grid Visual Meter */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.5rem',
          position: 'relative'
        }}
      >
        {STAGES.map((s, idx) => {
          const isDone = idx < activeIndex;
          const isActive = idx === activeIndex;
          const isPending = idx > activeIndex;
          const Icon = s.icon;

          let cardBg = '#ffffff';
          let borderColor = '#cbd5e1';
          let textColor = '#64748b';
          let badgeText = '○ Pending';
          let badgeBg = '#f1f5f9';
          let badgeColor = '#94a3b8';

          if (isDone) {
            cardBg = '#f0fdf4';
            borderColor = '#86efac';
            textColor = '#166534';
            badgeText = '✓ Done';
            badgeBg = '#dcfce7';
            badgeColor = '#15803d';
          } else if (isActive) {
            cardBg = '#f0fdfa';
            borderColor = '#0f766e';
            textColor = '#0f766e';
            badgeText = '● Active';
            badgeBg = '#ccfbf1';
            badgeColor = '#0f766e';
          }

          return (
            <div
              key={s.key}
              style={{
                background: cardBg,
                borderRadius: '8px',
                border: `2px solid ${borderColor}`,
                padding: '0.75rem 0.6rem',
                position: 'relative',
                boxShadow: isActive ? '0 0 0 3px rgba(15, 118, 110, 0.15)' : 'none',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: '115px'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.68rem', fontWeight: 700, color: textColor }}>
                    Stage {s.step}
                  </span>
                  <span
                    style={{
                      background: badgeBg,
                      color: badgeColor,
                      padding: '0.1rem 0.35rem',
                      borderRadius: '4px',
                      fontSize: '0.65rem',
                      fontWeight: 700
                    }}
                  >
                    {badgeText}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontWeight: 700, fontSize: '0.82rem', color: isPending ? '#64748b' : '#0f172a' }}>
                  <Icon size={14} color={isDone ? '#16a34a' : (isActive ? '#0f766e' : '#94a3b8')} />
                  {s.label}
                </div>

                <div style={{ fontSize: '0.7rem', color: isPending ? '#94a3b8' : '#475569', marginTop: '0.25rem', lineHeight: 1.3 }}>
                  {s.desc}
                </div>
              </div>

              {isActive && (
                <div style={{ marginTop: '0.4rem', borderTop: '1px solid #ccfbf1', paddingTop: '0.3rem', fontSize: '0.68rem', color: '#0f766e', fontWeight: 700 }}>
                  Current Operational State
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Messages Highlight Box */}
      {(complaint.admin_message || complaint.completion_message || complaint.notification_message || complaint.closure_message) && (
        <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {complaint.admin_message && (
            <div style={{ background: '#f0fdfa', border: '1px solid #99f6e4', padding: '0.6rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', color: '#134e4a' }}>
              <strong>📩 Administrator's Acceptance Message:</strong> "{complaint.admin_message}"
            </div>
          )}
          {complaint.completion_message && (
            <div style={{ background: '#f8fafc', border: '1px solid #cbd5e1', padding: '0.6rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', color: '#334155' }}>
              <strong>⚙️ Work Completion Report:</strong> "{complaint.completion_message}"
            </div>
          )}
          {complaint.notification_message && (
            <div style={{ background: '#f0fdf4', border: '1px solid #86efac', padding: '0.6rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', color: '#14532d' }}>
              <strong>✅ Resolution Notification to Citizen:</strong> "{complaint.notification_message}"
            </div>
          )}
          {complaint.closure_message && (
            <div style={{ background: '#f1f5f9', border: '1px solid #94a3b8', padding: '0.6rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', color: '#0f172a' }}>
              <strong>🔒 Formal Closure Notice:</strong> "{complaint.closure_message}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}
