import React, { useState, useEffect } from 'react';
import { Database, Building, Layers, Zap, Shield, GitBranch } from 'lucide-react';
import api from '../services/api';

export default function KnowledgeBaseViewer() {
  const [kb, setKb] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadKB() {
      try {
        const [kbData, deptData] = await Promise.all([
          api.getKnowledgeBase(),
          api.getDepartments(),
        ]);
        setKb(kbData);
        setDepartments(deptData);
      } catch (err) {
        console.error('Failed to load KB', err);
      } finally {
        setLoading(false);
      }
    }
    loadKB();
  }, []);

  if (loading) {
    return <div className="card"><p>Loading Knowledge Base...</p></div>;
  }

  return (
    <div>
      {/* Knowledge Base Header Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <Database size={20} color="#1e3a8a" />
              Classical AI Knowledge Representation & Ontology
            </h2>
            <p className="card-subtitle">
              Symbolic municipal domain model: Departments, capability constraints, category-issue taxonomy, and precedence hierarchies.
            </p>
          </div>
          <span className="badge badge-primary">
            Classical AI (No Black-Box Weights)
          </span>
        </div>

        <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
          <strong>Knowledge Representation Formalism:</strong> Ground Facts F, Production Rules R: (P1 &and; P2 &rarr; C), Constraint Domain D(Category) &rarr; {'{IssueTypes}'}, Precedence Lattice: CRITICAL &gt; HIGH &gt; MEDIUM &gt; LOW.
        </div>
      </div>

      {/* Section 1: Precedence Hierarchies */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
        <div className="card">
          <h3 className="card-title" style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>
            <Zap size={18} color="#c2410c" />
            Priority Precedence Lattice
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1rem' }}>
            When competing priority rules fire simultaneously, conflict resolution selects the supremum in the lattice:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '4px' }}>
              <strong>1. CRITICAL (Weight 4)</strong>
              <span>Immediate Life/Safety Threat</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '4px' }}>
              <strong>2. HIGH (Weight 3)</strong>
              <span>High Severity + Widespread Impact</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#fefce8', border: '1px solid #fef08a', borderRadius: '4px' }}>
              <strong>3. MEDIUM (Weight 2)</strong>
              <span>Noticeable Civic Impairment</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '4px' }}>
              <strong>4. LOW (Weight 1)</strong>
              <span>Standard Routine Grievance</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title" style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>
            <Shield size={18} color="#1e3a8a" />
            Escalation Precedence Order
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1rem' }}>
            Determines administrative dispatch urgency according to secondary forward chaining:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '4px' }}>
              <strong>1. IMMEDIATE (Tier 3)</strong>
              <span>Requires 24/7 Rapid Action Force</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '4px' }}>
              <strong>2. REQUIRED (Tier 2)</strong>
              <span>Escalated to Zonal Chief Engineer</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px' }}>
              <strong>3. NO_ESCALATION (Tier 1)</strong>
              <span>Standard Ward Level Processing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Department Capability Directory */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Building size={20} color="#1e3a8a" />
            Municipal Department Capability Matrix ({departments.length} Entities)
          </h3>
          <p className="card-subtitle">
            Every department defines verified issue capability domains and designated escalation authorities.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem' }}>
          {departments.map((d) => (
            <div
              key={d.department_id}
              style={{
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1e3a8a' }}>
                    {d.name}
                  </h4>
                  <span className="badge badge-primary">{d.department_id}</span>
                </div>
                <p style={{ fontSize: '0.82rem', color: '#475569', margin: '0.5rem 0' }}>
                  {d.description}
                </p>

                <div style={{ marginTop: '0.75rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
                    Supported Issues (Capability Domain):
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.35rem' }}>
                    {d.supported_issues?.map((iss, idx) => (
                      <span key={idx} className="badge badge-neutral" style={{ fontSize: '0.72rem' }}>
                        {iss.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid #f1f5f9', fontSize: '0.78rem', color: '#0f766e' }}>
                <strong>Escalation Authority:</strong> {d.escalation_authority}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 3: Category Taxonomy & CSP Constraints */}
      {kb?.taxonomy && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Layers size={20} color="#1e3a8a" />
              Taxonomy & Constraint Satisfaction Domains
            </h3>
            <p className="card-subtitle">
              Valid issue pairings for each category. Combinations outside this domain are rejected by CSP validation.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
            {Object.entries(kb.taxonomy).map(([cat, issues]) => (
              <div key={cat} style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                <h5 style={{ fontWeight: 700, color: '#0f172a', marginBottom: '0.4rem', borderBottom: '1px solid #cbd5e1', paddingBottom: '0.2rem' }}>
                  {cat}
                </h5>
                <ul style={{ paddingLeft: '1.25rem', fontSize: '0.8rem', color: '#475569' }}>
                  {issues.map((iss, i) => (
                    <li key={i}>{iss}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
