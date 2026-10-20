import React, { useState } from 'react';
import { KeyRound, Shield, AlertCircle, CheckCircle2, ArrowLeft, Eye, EyeOff, Lock, Send, RefreshCw } from 'lucide-react';
import api from '../services/api';
import logo from '../assets/logo.png';

export default function ForgotPassword({ onNavigateLogin }) {
  const [step, setStep] = useState(1); // 1: Email, 2: Code & New Password, 3: Success
  const [email, setEmail] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [demoCode, setDemoCode] = useState('');

  // Step 1: Request reset code
  const handleRequestCode = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    if (!email.trim()) {
      setErrorMsg('Please enter your email address.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.forgotPassword(email.trim());
      if (res.reset_code) {
        setDemoCode(res.reset_code);
      }
      setStep(2);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Failed to request password reset code. Please check your email.');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Submit new password with code
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!resetCode.trim()) {
      setErrorMsg('Please enter the 6-digit verification code.');
      return;
    }
    if (newPassword.length < 6) {
      setErrorMsg('New password must be at least 6 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setErrorMsg('Passwords do not match. Please re-check.');
      return;
    }

    setLoading(true);
    try {
      await api.resetPassword(email.trim(), resetCode.trim(), newPassword);
      setStep(3);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Failed to reset password. Please verify the code and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '460px', margin: '3.5rem auto', padding: '0 1rem' }}>
      <div className="card" style={{ borderTop: '4px solid #1e3a8a', padding: '2rem' }}>
        {/* Header Icon & Title */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-flex', padding: '0.4rem', background: '#f8fafc', borderRadius: '16px', marginBottom: '0.75rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <img src={logo} alt="CivicResolve Logo" style={{ width: '56px', height: '56px', objectFit: 'contain' }} />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
            CivicResolve
          </h2>
          <p style={{ fontSize: '0.88rem', fontWeight: 600, color: '#1e3a8a', marginTop: '0.2rem' }}>
            {step === 3 ? 'Password Updated Successfully' : 'Reset Account Password'}
          </p>
          <p style={{ fontSize: '0.83rem', color: '#64748b', marginTop: '0.2rem' }}>
            {step === 1 && 'Enter your registered email address to receive a verification code.'}
            {step === 2 && `Enter the 6-digit code sent for ${email} and choose a new password.`}
            {step === 3 && 'Your credentials have been securely updated.'}
          </p>
        </div>

        {/* Error Notification */}
        {errorMsg && (
          <div className="conflict-box blocking" style={{ marginBottom: '1.25rem' }}>
            <div className="conflict-title" style={{ color: '#991b1b', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <AlertCircle size={17} />
              Reset Error
            </div>
            <p style={{ fontSize: '0.84rem', margin: '0.2rem 0 0 0' }}>{errorMsg}</p>
          </div>
        )}

        {/* ============================================================== */}
        {/* STEP 1: Enter Email */}
        {/* ============================================================== */}
        {step === 1 && (
          <form onSubmit={handleRequestCode} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="reset-email">Registered Email Address *</label>
              <input
                id="reset-email"
                type="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                autoComplete="email"
                required
                autoFocus
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', marginTop: '0.5rem' }}>
              <Send size={16} />
              {loading ? 'Generating Code...' : 'Send Verification Code'}
            </button>

            <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
              <button
                type="button"
                onClick={onNavigateLogin}
                className="btn btn-secondary"
                style={{ width: '100%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}
              >
                <ArrowLeft size={15} /> Back to Sign In
              </button>
            </div>
          </form>
        )}

        {/* ============================================================== */}
        {/* STEP 2: Enter Reset Code & Set New Password */}
        {/* ============================================================== */}
        {step === 2 && (
          <form onSubmit={handleResetPassword} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Demo / Local Verification Code Banner */}
            {demoCode && (
              <div style={{ background: '#f0fdf4', border: '1px solid #86efac', padding: '0.75rem', borderRadius: '8px', fontSize: '0.82rem', color: '#166534' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>Security Verification Code: <strong>{demoCode}</strong></span>
                  <button
                    type="button"
                    onClick={() => setResetCode(demoCode)}
                    style={{ background: '#16a34a', color: '#ffffff', border: 'none', borderRadius: '4px', padding: '0.2rem 0.5rem', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer' }}
                  >
                    Auto-Fill
                  </button>
                </div>
                <small style={{ display: 'block', color: '#15803d', marginTop: '0.2rem' }}>
                  Valid for 15 minutes.
                </small>
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="reset-code">6-Digit Verification Code *</label>
              <input
                id="reset-code"
                type="text"
                className="form-input"
                value={resetCode}
                onChange={(e) => setResetCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="e.g. 123456"
                inputMode="numeric"
                maxLength={6}
                required
                autoFocus
                style={{ letterSpacing: '0.2em', fontSize: '1.1rem', fontWeight: 700, textAlign: 'center' }}
              />
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label className="form-label" htmlFor="new-password">New Password *</label>
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ background: 'none', border: 'none', color: '#64748b', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem', cursor: 'pointer', padding: 0 }}
                >
                  {showPassword ? <EyeOff size={13} /> : <Eye size={13} />}
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              <input
                id="new-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 6 characters"
                autoComplete="new-password"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirm-password">Confirm New Password *</label>
              <input
                id="confirm-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your new password"
                autoComplete="new-password"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', marginTop: '0.5rem' }}>
              <Lock size={16} />
              {loading ? 'Updating Password...' : 'Reset Password'}
            </button>

            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.5rem', marginTop: '0.25rem' }}>
              <button
                type="button"
                onClick={() => setStep(1)}
                className="btn btn-secondary"
                style={{ flex: 1, fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
              >
                Change Email
              </button>
              <button
                type="button"
                onClick={handleRequestCode}
                className="btn btn-secondary"
                style={{ flex: 1, fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                disabled={loading}
              >
                <RefreshCw size={13} /> Resend Code
              </button>
            </div>
          </form>
        )}

        {/* ============================================================== */}
        {/* STEP 3: Success Confirmation */}
        {/* ============================================================== */}
        {step === 3 && (
          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
            <div style={{ display: 'inline-flex', padding: '1rem', background: '#dcfce7', borderRadius: '50%', color: '#16a34a', marginBottom: '1rem' }}>
              <CheckCircle2 size={40} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#15803d', margin: '0 0 0.5rem 0' }}>
              Password Reset Successfully!
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              Your account password for <strong>{email}</strong> has been updated. You can now use your new password to sign in to the civic portal.
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={onNavigateLogin}
              style={{ width: '100%' }}
            >
              Proceed to Sign In &rarr;
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
