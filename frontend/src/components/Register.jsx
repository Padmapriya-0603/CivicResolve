import React, { useState } from 'react';
import { UserPlus, Shield, ArrowLeft, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';

export default function Register({ onNavigateLogin }) {
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (password !== confirmPw) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await register(name, email, password, phone);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '480px', margin: '3rem auto' }}>
      <div className="card" style={{ borderTop: '4px solid #1e3a8a', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-flex', padding: '0.4rem', background: '#f8fafc', borderRadius: '16px', marginBottom: '0.75rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <img src={logo} alt="CivicResolve Logo" style={{ width: '56px', height: '56px', objectFit: 'contain' }} />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
            CivicResolve
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.25rem' }}>
            Citizen Account Registration &bull; Smart Complaints, Clear Decisions
          </p>
        </div>

        {errorMsg && (
          <div className="conflict-box blocking" style={{ marginBottom: '1.25rem' }}>
            <div className="conflict-title" style={{ color: '#991b1b' }}>
              <AlertCircle size={18} />
              Registration Constraint Failure
            </div>
            <p style={{ fontSize: '0.85rem' }}>{errorMsg}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input
              type="text"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Priya Verma"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address *</label>
            <input
              type="text"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. priya@example.com"
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

          <div className="form-group">
            <label className="form-label">Password * (Min 6 chars)</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password *</label>
            <input
              type="password"
              className="form-input"
              value={confirmPw}
              onChange={(e) => setConfirmPw(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', marginTop: '0.5rem' }}>
            {loading ? 'Creating Account...' : 'Register Citizen Account'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.25rem', fontSize: '0.85rem', color: '#64748b' }}>
          Already have an account?{' '}
          <button
            type="button"
            onClick={onNavigateLogin}
            style={{ background: 'none', border: 'none', color: '#1e3a8a', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
}
