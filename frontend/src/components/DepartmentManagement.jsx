import React, { useState, useEffect } from 'react';
import { Building, Plus, Edit2, Shield, CheckCircle, RefreshCw } from 'lucide-react';
import api from '../services/api';

export default function DepartmentManagement() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    department_id: '',
    name: '',
    description: '',
    supported_issues: '',
    escalation_authority: '',
    is_active: true,
  });

  const loadDepartments = async () => {
    setLoading(true);
    try {
      const data = await api.getDepartments();
      setDepartments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  const openCreateModal = () => {
    setIsEditing(false);
    setFormData({
      department_id: `DEPT_${Date.now().toString().slice(-4)}`,
      name: '',
      description: '',
      supported_issues: '',
      escalation_authority: 'Municipal Commissioner',
      is_active: true,
    });
    setShowModal(true);
  };

  const openEditModal = (d) => {
    setIsEditing(true);
    setFormData({
      department_id: d.department_id,
      name: d.name,
      description: d.description,
      supported_issues: Array.isArray(d.supported_issues) ? d.supported_issues.join(', ') : '',
      escalation_authority: d.escalation_authority,
      is_active: d.is_active,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const issueList = formData.supported_issues
      .split(',')
      .map(s => s.trim().toLowerCase().replace(/ /g, '_'))
      .filter(s => s.length > 0);

    try {
      if (isEditing) {
        await api.updateDepartment(formData.department_id, {
          name: formData.name,
          description: formData.description,
          supported_issues: issueList,
          escalation_authority: formData.escalation_authority,
          is_active: formData.is_active,
        });
      } else {
        await api.createDepartment({
          department_id: formData.department_id,
          name: formData.name,
          description: formData.description,
          supported_issues: issueList,
          escalation_authority: formData.escalation_authority,
          is_active: formData.is_active,
        });
      }
      setShowModal(false);
      loadDepartments();
      alert(`Department ${isEditing ? 'updated' : 'created'} successfully.`);
    } catch (err) {
      alert(`Operation failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleToggleActive = async (dept) => {
    const nextState = !dept.is_active;
    const msg = nextState
      ? `Activate department '${dept.name}'?`
      : `Soft-deactivate department '${dept.name}'? It will no longer receive new automated complaint routings.`;
    if (!window.confirm(msg)) return;

    try {
      await api.updateDepartment(dept.department_id, { is_active: nextState });
      loadDepartments();
    } catch (err) {
      alert(`Failed to update department status: ${err.message}`);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <Building size={20} color="#1e3a8a" />
            Municipal Department Registry
          </h2>
          <p className="card-subtitle">
            Configure department capabilities, supported issue types, escalation authorities, and operational status.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-primary" onClick={openCreateModal}>
            <Plus size={16} /> Add Department
          </button>
          <button className="btn btn-secondary" onClick={loadDepartments} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        </div>
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
              justifyContent: 'space-between',
              boxShadow: 'var(--shadow-sm)',
              opacity: d.is_active ? 1 : 0.65
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1e3a8a' }}>
                  {d.name}
                </h3>
                <span className={`badge ${d.is_active ? 'badge-low' : 'badge-critical'}`}>
                  {d.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Code: {d.department_id}</span>
              <p style={{ fontSize: '0.85rem', color: '#475569', margin: '0.5rem 0' }}>
                {d.description}
              </p>

              <div style={{ marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  Supported Issue Types:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem', marginTop: '0.3rem' }}>
                  {d.supported_issues?.map((iss, i) => (
                    <span key={i} className="badge badge-neutral" style={{ fontSize: '0.72rem' }}>
                      {iss.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#0f766e' }}>
                <strong>Authority:</strong> {d.escalation_authority}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.4rem', marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid #f1f5f9' }}>
              <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }} onClick={() => openEditModal(d)}>
                <Edit2 size={13} /> Edit
              </button>
              <button
                className={`btn ${d.is_active ? 'btn-secondary' : 'btn-primary'}`}
                style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                onClick={() => handleToggleActive(d)}
              >
                {d.is_active ? 'Soft Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Create/Edit Department */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '540px', maxWidth: '90%', margin: 0, boxShadow: 'var(--shadow-lg)' }}>
            <div className="card-header">
              <h3 className="card-title">
                <Building size={18} />
                {isEditing ? 'Edit Department' : 'Create New Department'}
              </h3>
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Department Identifier Code *</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.department_id}
                  disabled={isEditing}
                  onChange={(e) => setFormData(prev => ({ ...prev, department_id: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Department Name *</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description *</label>
                <textarea
                  className="form-input"
                  rows="2"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Supported Issue Types (Comma separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. pothole, damaged_road, blocked_road"
                  value={formData.supported_issues}
                  onChange={(e) => setFormData(prev => ({ ...prev, supported_issues: e.target.value }))}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Designated Escalation Authority *</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.escalation_authority}
                  onChange={(e) => setFormData(prev => ({ ...prev, escalation_authority: e.target.value }))}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">
                  {isEditing ? 'Save Changes' : 'Create Department'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
