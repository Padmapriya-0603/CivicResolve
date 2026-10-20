import React, { useState } from 'react';
import { LogIn, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';

export default function Login({ onNavigateRegister, onNavigateForgotPassword }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '440px', margin: '3.5rem auto' }}>
      <div className="card" style={{ borderTop: '4px solid #1e3a8a', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-flex', padding: '0.4rem', background: '#f8fafc', borderRadius: '16px', marginBottom: '0.75rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <img src={logo} alt="CivicResolve Logo" style={{ width: '64px', height: '64px', objectFit: 'contain' }} />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
            CivicResolve
          </h2>
          <p style={{ fontSize: '0.88rem', color: '#64748b', marginTop: '0.35rem', fontWeight: 500 }}>
            Smart Complaints. Clear Decisions. Better Governance
          </p>
        </div>

        {errorMsg && (
          <div className="conflict-box blocking" style={{ marginBottom: '1.25rem' }}>
            <div className="conflict-title" style={{ color: '#991b1b' }}>
              <AlertCircle size={18} />
              Authentication Failure
            </div>
            <p style={{ fontSize: '0.85rem' }}>{errorMsg}</p>
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="text"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
              <label className="form-label" htmlFor="login-password" style={{ margin: 0 }}>Password</label>
              <button
                type="button"
                onClick={onNavigateForgotPassword}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#1e3a8a',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  padding: 0,
                  textDecoration: 'underline'
                }}
              >
                Forgot Password?
              </button>
            </div>
            <input
              id="login-password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', marginTop: '0.5rem' }}>
            <LogIn size={16} />
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.25rem', fontSize: '0.85rem', color: '#64748b' }}>
          Are you a citizen without an account?{' '}
          <button
            type="button"
            onClick={onNavigateRegister}
            style={{ background: 'none', border: 'none', color: '#1e3a8a', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
          >
            Register Here
          </button>
        </div>

        {/* Quick Demo Role Logins */}
        <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.6rem', textAlign: 'center' }}>
            Quick Demo Logins (Click to Fill)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.4rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('priya@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#0f766e' }}>Citizen</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>priya@gmail.com</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('admin@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#b45309' }}>Administrator</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>admin@gmail.com</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('officer.roads@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#1e3a8a' }}>Officer (Roads)</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>officer.roads@...</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('officer.water@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#0284c7' }}>Officer (Water)</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>officer.water@...</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('officer.sanitation@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#16a34a' }}>Officer (Sanitation)</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>officer.sanitation@...</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('officer.lighting@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#d97706' }}>Officer (Lighting)</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>officer.lighting@...</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              style={{ gridColumn: 'span 2', fontSize: '0.75rem', padding: '0.35rem 0.5rem', textAlign: 'left', display: 'flex', flexDirection: 'column' }}
              onClick={() => { setEmail('officer.drainage@gmail.com'); setPassword('123456'); }}
            >
              <strong style={{ color: '#7c3aed' }}>Officer (Drainage)</strong>
              <span style={{ fontSize: '0.68rem', color: '#64748b' }}>officer.drainage@gmail.com</span>
            </button>
          </div>
          <div style={{ textAlign: 'center', fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.5rem' }}>
            Password for all accounts: <code>123456</code>
          </div>
        </div>
      </div>
    </div>
  );
}
