import React from 'react';
import { AlertTriangle, AlertCircle, ShieldAlert, CheckCircle } from 'lucide-react';

export default function ConflictPanel({ conflicts = [] }) {
  if (!conflicts || conflicts.length === 0) {
    return (
      <div className="card" style={{ borderLeft: '4px solid #16a34a' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: '#15803d' }}>
          <CheckCircle size={20} />
          <strong>Zero Contradictions Detected:</strong> All input facts and inferential conclusions satisfy consistency constraints.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title" style={{ color: '#b45309' }}>
            <AlertTriangle size={20} />
            Constraint & Conflict Evaluation Panel ({conflicts.length})
          </h3>
          <p className="card-subtitle">
            Formal audit of semantic contradictions, domain mismatches, or competing rule conclusions.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {conflicts.map((c, idx) => {
          const isBlocking = c.is_blocking;
          return (
            <div key={idx} className={`conflict-box ${isBlocking ? 'blocking' : ''}`}>
              <div className="conflict-title" style={{ color: isBlocking ? '#991b1b' : '#92400e' }}>
                {isBlocking ? <ShieldAlert size={18} /> : <AlertCircle size={18} />}
                <span>
                  {c.conflict_type?.replace(/_/g, ' ') || 'DETECTED CONFLICT'}
                  {isBlocking && ' — [DECISION BLOCKED]'}
                </span>
              </div>
              <p style={{ fontSize: '0.88rem', color: '#334155', marginBottom: '0.5rem' }}>
                {c.description}
              </p>

              {c.conflicting_elements && c.conflicting_elements.length > 0 && (
                <div style={{ fontSize: '0.82rem', marginBottom: '0.5rem' }}>
                  <strong>Conflicting Elements:</strong>
                  <ul style={{ paddingLeft: '1.25rem', marginTop: '0.2rem', color: '#475569' }}>
                    {c.conflicting_elements.map((el, i) => (
                      <li key={i}>{el}</li>
                    ))}
                  </ul>
                </div>
              )}

              {c.resolution && (
                <div style={{ fontSize: '0.82rem', background: 'rgba(255,255,255,0.7)', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid rgba(0,0,0,0.06)' }}>
                  <strong>Formal Resolution:</strong> {c.resolution}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
