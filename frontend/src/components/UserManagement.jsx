import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Search, ShieldCheck, Check, X, Edit2, AlertTriangle, Building, RefreshCw } from 'lucide-react';
import api from '../services/api';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  // Create User Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUserData, setNewUserData] = useState({
    name: '',
    email: '',
    phone: '',
    password: 'Officer@1234',
    role: 'DEPARTMENT_OFFICER',
    department_id: '',
  });

  // Role Change Modal
  const [selectedUserForRole, setSelectedUserForRole] = useState(null);
  const [newRole, setNewRole] = useState('CITIZEN');
  const [newDeptId, setNewDeptId] = useState('');
  const [confirmRoleChange, setConfirmRoleChange] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [uList, dList] = await Promise.all([
        api.getUsers({ search, role: roleFilter, department_id: deptFilter }),
        api.getDepartments(),
      ]);
      setUsers(uList);
      setDepartments(dList);
      if (dList.length > 0 && !newUserData.department_id) {
        setNewUserData(prev => ({ ...prev, department_id: dList[0].department_id }));
      }
    } catch (err) {
      console.error('Failed to load users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [roleFilter, deptFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const handleToggleStatus = async (user) => {
    const nextState = !user.is_active;
    const confirmMsg = nextState
      ? `Are you sure you want to activate user '${user.name}'?`
      : `Are you sure you want to DEACTIVATE user '${user.name}'? They will be blocked from logging in.`;

    if (!window.confirm(confirmMsg)) return;

    try {
      await api.updateUserStatus(user.id, nextState);
      loadData();
    } catch (err) {
      alert(`Operation failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleCreateUserSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.createUser(newUserData);
      setShowCreateModal(false);
      setNewUserData({
        name: '',
        email: '',
        phone: '',
        password: 'Officer@1234',
        role: 'DEPARTMENT_OFFICER',
        department_id: departments[0]?.department_id || '',
      });
      loadData();
      alert('User created successfully.');
    } catch (err) {
      alert(`Failed to create user: ${err.response?.data?.detail || err.message}`);
    }
  };

  const openRoleModal = (u) => {
    setSelectedUserForRole(u);
    setNewRole(u.role);
    setNewDeptId(u.department_id || (departments[0]?.department_id || ''));
    setConfirmRoleChange(false);
  };

  const handleRoleChangeSubmit = async (e) => {
    e.preventDefault();
    if (!confirmRoleChange) {
      alert('Please check the confirmation box to confirm this critical security role change.');
      return;
    }

    try {
      await api.updateUserRole(selectedUserForRole.id, newRole, newRole === 'DEPARTMENT_OFFICER' ? newDeptId : null);
      setSelectedUserForRole(null);
      loadData();
      alert('User role and department updated successfully.');
    } catch (err) {
      alert(`Role update failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN': return <span className="badge badge-critical">ADMIN</span>;
      case 'DEPARTMENT_OFFICER': return <span className="badge badge-high">OFFICER</span>;
      default: return <span className="badge badge-neutral">CITIZEN</span>;
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <Users size={20} color="#1e3a8a" />
            User Management & Administrative Access Control
          </h2>
          <p className="card-subtitle">
            Manage user roles, activate/deactivate accounts, assign officers to departments, and enforce least-privilege security policies.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            <UserPlus size={16} /> Add Officer / Admin
          </button>
          <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.4rem' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary" style={{ padding: '0.5rem 0.75rem' }}>
            <Search size={16} />
          </button>
        </form>

        <select
          className="form-select"
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
        >
          <option value="">All Roles</option>
          <option value="CITIZEN">Citizen</option>
          <option value="DEPARTMENT_OFFICER">Department Officer</option>
          <option value="ADMIN">Administrator</option>
        </select>

        <select
          className="form-select"
          value={deptFilter}
          onChange={(e) => setDeptFilter(e.target.value)}
        >
          <option value="">All Departments</option>
          {departments.map((d) => (
            <option key={d.department_id} value={d.department_id}>{d.name}</option>
          ))}
        </select>
      </div>

      {/* Users Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Assigned Department</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} style={{ opacity: u.is_active ? 1 : 0.6 }}>
                <td><strong>#{u.id}</strong></td>
                <td>
                  <div style={{ fontWeight: 600 }}>{u.name}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{u.phone || 'No phone'}</div>
                </td>
                <td>{u.email}</td>
                <td>{getRoleBadge(u.role)}</td>
                <td>
                  {u.role === 'DEPARTMENT_OFFICER' ? (
                    <span style={{ fontWeight: 600, color: '#1e3a8a' }}>
                      {u.department_name || u.department_id || 'Unassigned'}
                    </span>
                  ) : (
                    <span style={{ color: '#94a3b8' }}>—</span>
                  )}
                </td>
                <td>
                  {u.is_active ? (
                    <span className="badge badge-low">Active</span>
                  ) : (
                    <span className="badge badge-critical">Deactivated</span>
                  )}
                </td>
                <td style={{ fontSize: '0.78rem', color: '#64748b' }}>
                  {u.created_at ? u.created_at.split(' ')[0] : 'N/A'}
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '0.35rem' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem' }}
                      onClick={() => openRoleModal(u)}
                    >
                      <Edit2 size={13} /> Change Role
                    </button>
                    <button
                      className={`btn ${u.is_active ? 'btn-secondary' : 'btn-primary'}`}
                      style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem' }}
                      onClick={() => handleToggleStatus(u)}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal: Create User */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0, boxShadow: 'var(--shadow-lg)' }}>
            <div className="card-header">
              <h3 className="card-title"><UserPlus size={18} /> Create Officer or Administrator</h3>
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateUserSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Full Name *</label>
                <input
                  type="text"
                  className="form-input"
                  value={newUserData.name}
                  onChange={(e) => setNewUserData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address *</label>
                <input
                  type="text"
                  className="form-input"
                  value={newUserData.email}
                  onChange={(e) => setNewUserData(prev => ({ ...prev, email: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Temporary Password *</label>
                <input
                  type="password"
                  className="form-input"
                  value={newUserData.password}
                  onChange={(e) => setNewUserData(prev => ({ ...prev, password: e.target.value }))}
                  required
                  minLength={6}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Role *</label>
                <select
                  className="form-select"
                  value={newUserData.role}
                  onChange={(e) => setNewUserData(prev => ({ ...prev, role: e.target.value }))}
                >
                  <option value="DEPARTMENT_OFFICER">DEPARTMENT_OFFICER</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>

              {newUserData.role === 'DEPARTMENT_OFFICER' && (
                <div className="form-group">
                  <label className="form-label">Assign Department *</label>
                  <select
                    className="form-select"
                    value={newUserData.department_id}
                    onChange={(e) => setNewUserData(prev => ({ ...prev, department_id: e.target.value }))}
                  >
                    {departments.map((d) => (
                      <option key={d.department_id} value={d.department_id}>{d.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Account</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Change Role & Department with Confirmation */}
      {selectedUserForRole && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '520px', maxWidth: '90%', margin: 0, boxShadow: 'var(--shadow-lg)', borderTop: '4px solid #d97706' }}>
            <div className="card-header">
              <h3 className="card-title">
                <AlertTriangle size={18} color="#d97706" />
                Change User Role: {selectedUserForRole.name}
              </h3>
              <button className="btn btn-secondary" onClick={() => setSelectedUserForRole(null)}>✕</button>
            </div>

            <form onSubmit={handleRoleChangeSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ fontSize: '0.85rem', color: '#475569', background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                <p>Current Role: <strong>{selectedUserForRole.role}</strong></p>
                <p>Email: <strong>{selectedUserForRole.email}</strong></p>
              </div>

              <div className="form-group">
                <label className="form-label">Assign New Role</label>
                <select
                  className="form-select"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                >
                  <option value="CITIZEN">CITIZEN (Self-service only)</option>
                  <option value="DEPARTMENT_OFFICER">DEPARTMENT_OFFICER (Department queue access)</option>
                  <option value="ADMIN">ADMIN (Full administrative privileges)</option>
                </select>
              </div>

              {newRole === 'DEPARTMENT_OFFICER' && (
                <div className="form-group">
                  <label className="form-label">Assign Department</label>
                  <select
                    className="form-select"
                    value={newDeptId}
                    onChange={(e) => setNewDeptId(e.target.value)}
                  >
                    {departments.map((d) => (
                      <option key={d.department_id} value={d.department_id}>{d.name}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Explicit Confirmation Checkbox (Section 53) */}
              <div style={{ background: '#fffbeb', border: '1px solid #fde68a', padding: '0.75rem', borderRadius: '6px' }}>
                <label className="form-checkbox-label" style={{ color: '#92400e', fontSize: '0.85rem' }}>
                  <input
                    type="checkbox"
                    checked={confirmRoleChange}
                    onChange={(e) => setConfirmRoleChange(e.target.checked)}
                  />
                  <span>
                    <strong>Security Confirmation:</strong> I confirm modifying authorization for this user. The system will prevent removing the last active administrator.
                  </span>
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setSelectedUserForRole(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={!confirmRoleChange}>
                  Confirm Role Change
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
