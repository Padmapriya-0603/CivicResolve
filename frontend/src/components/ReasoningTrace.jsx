import React, { useState } from 'react';
import { GitCommit, ArrowDown, Check, Code, ShieldCheck, HelpCircle } from 'lucide-react';

export default function ReasoningTrace({ trace = [], explanation = '', missingInfo = [] }) {
  const [showRawExplanation, setShowRawExplanation] = useState(false);

  if (!trace || trace.length === 0) {
    return (
      <div className="card">
        <p style={{ color: '#64748b' }}>No reasoning trace steps recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">
            <GitCommit size={20} color="#1e3a8a" />
            Deterministic Inference Chain & Reasoning Trace
          </h3>
          <p className="card-subtitle">
            Formal Forward Chaining deduction trace showing precondition evaluation, fired production rules, and derived facts.
          </p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={() => setShowRawExplanation(!showRawExplanation)}
          style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
        >
          <Code size={14} />
          {showRawExplanation ? 'Hide Audit Log' : 'View Audit Log'}
        </button>
      </div>

      {/* Missing Information Callout */}
      {missingInfo && missingInfo.length > 0 && (
        <div style={{ background: '#f8fafc', border: '1px solid #cbd5e1', borderLeft: '4px solid #64748b', padding: '0.85rem 1rem', borderRadius: '6px', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '0.88rem', color: '#334155' }}>
            <HelpCircle size={16} />
            Missing Information Notice (Zero Guessing Policy):
          </div>
          <ul style={{ paddingLeft: '1.25rem', marginTop: '0.3rem', fontSize: '0.82rem', color: '#475569' }}>
            {missingInfo.map((info, idx) => (
              <li key={idx}>{info}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Raw Explanation Box */}
      {showRawExplanation && explanation && (
        <pre className="code-box" style={{ marginBottom: '1.5rem', whiteSpace: 'pre-wrap' }}>
          {explanation}
        </pre>
      )}

      {/* Visual Step-by-Step Inference Pipeline */}
      <div className="trace-timeline">
        {trace.map((step, idx) => {
          const isRuleFire = step.step_type === 'RULE_FIRE';
          const isArbitration = step.step_type === 'PRIORITY_ARBITRATION';
          const isFinal = step.step_type === 'FINAL_DECISION';
          const isInput = step.step_type === 'INPUT_FACTS';

          let stepClass = 'trace-step';
          if (isRuleFire) stepClass += ' rule-fire';
          if (isArbitration) stepClass += ' priority-arbitration';
          if (isFinal) stepClass += ' final-decision';

          return (
            <div key={idx} className={stepClass}>
              <div className="step-header">
                <span className="step-order">STEP {step.step_order} • {step.step_type.replace(/_/g, ' ')}</span>
                {step.rule_id && (
                  <span className="badge badge-primary">
                    RULE {step.rule_id}
                  </span>
                )}
              </div>

              <div className="step-title">
                {step.rule_name ? step.rule_name : (isFinal ? 'Final Deterministic Disposition' : (isInput ? 'Percept Ground Facts' : 'Inference Step'))}
              </div>

              <p style={{ fontSize: '0.88rem', color: '#334155', margin: '0.4rem 0' }}>
                {step.explanation}
              </p>

              {/* Conditions Evaluated */}
              {step.conditions_evaluated && Object.keys(step.conditions_evaluated).length > 0 && (
                <div style={{ marginTop: '0.5rem', background: '#f8fafc', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #e2e8f0', fontSize: '0.8rem' }}>
                  <div style={{ fontWeight: 600, color: '#475569', marginBottom: '0.2rem' }}>Conditions Evaluated:</div>
                  {Object.entries(step.conditions_evaluated).map(([cond, status], i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#334155' }}>
                      <Check size={12} color="#16a34a" />
                      <span><code>{cond}</code> &rarr; {typeof status === 'object' ? `Value: ${JSON.stringify(status.actual_value)} [Satisfied]` : String(status)}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Derived Fact */}
              {step.derived_fact && Object.keys(step.derived_fact).length > 0 && (
                <div style={{ marginTop: '0.4rem', fontSize: '0.82rem', color: '#0f766e', fontWeight: 600 }}>
                  Asserted to Working Memory: {JSON.stringify(step.derived_fact)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
