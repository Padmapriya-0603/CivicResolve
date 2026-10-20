import React, { useState } from 'react';
import { User, Shield, Phone, Mail, Building, Save, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    try {
      await api.updateProfile({ name, phone });
      await refreshUser();
      setSuccessMsg('Profile updated successfully.');
    } catch (err) {
      alert(`Failed to update profile: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN': return <span className="badge badge-critical">ADMINISTRATOR</span>;
      case 'DEPARTMENT_OFFICER': return <span className="badge badge-high">DEPARTMENT OFFICER</span>;
      default: return <span className="badge badge-primary">CITIZEN</span>;
    }
  };

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <User size={20} color="#1e3a8a" />
              User Profile & Account Security
            </h2>
            <p className="card-subtitle">
              View authenticated role privileges and update allowed personal contact details.
            </p>
          </div>
          {getRoleBadge(user?.role)}
        </div>

        {successMsg && (
          <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '0.75rem', borderRadius: '6px', color: '#166534', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.88rem' }}>
            <CheckCircle size={16} /> {successMsg}
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Read-Only Role & Auth Information */}
          <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
            <div>
              <span className="stat-label">Security Role</span>
              <p style={{ fontWeight: 700, marginTop: '0.2rem' }}>{user?.role}</p>
              <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Assigned by System Administrator</span>
            </div>

            <div>
              <span className="stat-label">Email Address</span>
              <p style={{ fontWeight: 700, marginTop: '0.2rem' }}>{user?.email}</p>
              <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Primary authentication key</span>
            </div>

            {user?.role === 'DEPARTMENT_OFFICER' && (
              <div style={{ gridColumn: '1 / -1' }}>
                <span className="stat-label">Department Assignment</span>
                <p style={{ fontWeight: 700, color: '#1e3a8a', marginTop: '0.2rem' }}>
                  {user?.department_name || user?.department_id}
                </p>
                <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                  Restricts access strictly to this department's complaints
                </span>
              </div>
            )}
          </div>

          {/* Editable Contact Fields */}
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input
              type="text"
              className="form-input"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="e.g. +91 98765 43210"
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              <Save size={16} />
              {saving ? 'Saving Changes...' : 'Save Profile Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
