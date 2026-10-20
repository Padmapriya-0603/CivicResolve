import React, { useState, useEffect } from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
  useNavigate,
  useLocation,
  useParams
} from 'react-router-dom';
import {
  LayoutDashboard,
  Send,
  History,
  Building,
  BarChart3,
  Cpu,
  Shield,
  Users,
  LogOut,
  User,
  ShieldCheck,
  FileText,
  Bell,
  ArrowLeft
} from 'lucide-react';

import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ForgotPassword from './components/ForgotPassword';
import logo from './assets/logo.png';
import CitizenDashboard from './components/CitizenDashboard';
import OfficerDashboard from './components/OfficerDashboard';
import AdminDashboard from './components/AdminDashboard';
import UserManagement from './components/UserManagement';
import DepartmentManagement from './components/DepartmentManagement';
import AuditLogViewer from './components/AuditLogViewer';
import Profile from './components/Profile';
import ComplaintForm from './components/ComplaintForm';
import ComplaintHistory from './components/ComplaintHistory';
import ComplaintDetails from './components/ComplaintDetails';
import Statistics from './components/Statistics';
import api from './services/api';

// ==========================================
// Protected & Role-Based Route Wrappers
// ==========================================
function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, role, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f8fafc' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spin" style={{ display: 'inline-block', marginBottom: '1rem' }}>
            <Shield size={40} color="#1e3a8a" />
          </div>
          <p style={{ color: '#475569', fontWeight: 600 }}>Verifying Session Credentials...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    if (role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
    if (role === 'DEPARTMENT_OFFICER') return <Navigate to="/officer/dashboard" replace />;
    return <Navigate to="/citizen/dashboard" replace />;
  }

  return children;
}

// Wrapper to pass URL parameter `:id` directly to ComplaintDetails
function ComplaintDetailsRoute({ defaultBack }) {
  const { id } = useParams();
  const navigate = useNavigate();
  return (
    <ComplaintDetails
      complaintId={id}
      onBack={() => navigate(defaultBack)}
    />
  );
}

// ==========================================
// Dedicated Notifications View (Section 43 & 89)
// ==========================================
function NotificationsView() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadNotifs = async () => {
    setLoading(true);
    try {
      const res = await api.getNotifications();
      setNotifications(res.notifications || []);
    } catch (e) {
      console.error('Failed to load notifications', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifs();
  }, []);

  const handleMarkAll = async () => {
    try {
      await api.markAllNotificationsRead();
      loadNotifs();
    } catch (e) {
      console.error(e);
    }
  };

  const handleMarkOne = async (id, complaintId) => {
    try {
      await api.markNotificationRead(id);
      if (complaintId) {
        navigate(`/citizen/complaints/${complaintId}`);
      } else {
        loadNotifs();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <Bell size={20} color="#1e3a8a" />
            Notifications
          </h2>
          <p className="card-subtitle">
            Official municipal alerts transmitted across the 5-stage grievance lifecycle.
          </p>
        </div>
        {notifications.some(n => !n.is_read) && (
          <button className="btn btn-secondary" onClick={handleMarkAll} style={{ fontSize: '0.8rem' }}>
            Mark All as Read
          </button>
        )}
      </div>

      {loading ? (
        <p>Loading notifications...</p>
      ) : notifications.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', color: '#64748b' }}>
          <Bell size={36} color="#cbd5e1" style={{ marginBottom: '0.75rem' }} />
          <p style={{ fontWeight: 600 }}>No notifications at this time.</p>
          <p style={{ fontSize: '0.82rem' }}>You will receive updates here as municipal administration processes your grievances.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => handleMarkOne(n.id, n.complaint_id)}
              style={{
                padding: '1rem',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                background: n.is_read ? '#f8fafc' : '#eff6ff',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                transition: 'background 0.2s ease'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a' }}>{n.title}</span>
                  {!n.is_read && <span className="badge badge-high" style={{ fontSize: '0.65rem' }}>NEW</span>}
                </div>
                <p style={{ margin: 0, fontSize: '0.85rem', color: '#334155' }}>{n.message}</p>
                <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem', display: 'inline-block' }}>{n.created_at}</span>
              </div>
              {n.complaint_id && (
                <span style={{ fontSize: '0.8rem', color: '#2563eb', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  Inspect #{n.complaint_id} &rarr;
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ==========================================
// Root Layout Navigation & Shell
// ==========================================
function MainLayout() {
  const { user, role, logout, isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [unreadNotifs, setUnreadNotifs] = useState(0);

  const isAdmin = role === 'ADMIN';
  const isOfficer = role === 'DEPARTMENT_OFFICER';
  const isCitizen = role === 'CITIZEN';

  useEffect(() => {
    if (isCitizen && isAuthenticated) {
      api.getNotifications()
        .then(res => setUnreadNotifs(res.unread_count || 0))
        .catch(() => {});
    }
  }, [location.pathname, isCitizen, isAuthenticated]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f8fafc' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spin" style={{ display: 'inline-block', marginBottom: '1rem' }}>
            <Shield size={40} color="#1e3a8a" />
          </div>
          <p style={{ color: '#475569', fontWeight: 600 }}>Loading Civic Security Portal...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const isActive = (path) => {
    if (path === '/citizen/dashboard' || path === '/admin/dashboard' || path === '/officer/dashboard') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div>
      {/* Header Bar */}
      <header className="header-bar">
        <div className="header-inner">
          <div className="brand-section">
            <div style={{ background: '#ffffff', padding: '0.25rem', borderRadius: '8px', display: 'flex', alignItems: 'center' }}>
              <img src={logo} alt="CivicResolve Logo" style={{ width: '28px', height: '28px', objectFit: 'contain' }} />
            </div>
            <div>
              <div className="brand-title">CivicResolve</div>
              <div className="brand-subtitle">
                {isAdmin ? 'System Administrator Console' : (isOfficer ? `${user?.department_name || 'Officer'} Queue` : 'Citizen Civic Portal')}
              </div>
            </div>
          </div>

          {/* Navigation Links based on Role (Section 43) */}
          <nav className="nav-links">
            {/* Citizen Nav */}
            {isCitizen && (
              <>
                <Link
                  to="/citizen/dashboard"
                  className={`nav-btn ${isActive('/citizen/dashboard') ? 'active' : ''}`}
                >
                  <LayoutDashboard size={16} />
                  Dashboard
                </Link>
                <Link
                  to="/citizen/complaints/new"
                  className={`nav-btn ${isActive('/citizen/complaints/new') ? 'active' : ''}`}
                >
                  <Send size={16} />
                  Submit Grievance
                </Link>
                <Link
                  to="/citizen/complaints"
                  className={`nav-btn ${isActive('/citizen/complaints') && !isActive('/citizen/complaints/new') ? 'active' : ''}`}
                >
                  <History size={16} />
                  My Grievances
                </Link>
                <Link
                  to="/citizen/notifications"
                  className={`nav-btn ${isActive('/citizen/notifications') ? 'active' : ''}`}
                  style={{ position: 'relative' }}
                >
                  <Bell size={16} />
                  Notifications
                  {unreadNotifs > 0 && (
                    <span
                      style={{
                        position: 'absolute',
                        top: '-4px',
                        right: '-4px',
                        background: '#dc2626',
                        color: '#ffffff',
                        fontSize: '0.65rem',
                        fontWeight: 800,
                        padding: '1px 5px',
                        borderRadius: '999px',
                        lineHeight: '1.2'
                      }}
                    >
                      {unreadNotifs}
                    </span>
                  )}
                </Link>
              </>
            )}

            {/* Admin Nav (Section 43) */}
            {isAdmin && (
              <>
                <Link
                  to="/admin/dashboard"
                  className={`nav-btn ${isActive('/admin/dashboard') ? 'active' : ''}`}
                >
                  <LayoutDashboard size={16} />
                  Dashboard
                </Link>
                <Link
                  to="/admin/complaints"
                  className={`nav-btn ${isActive('/admin/complaints') ? 'active' : ''}`}
                >
                  <History size={16} />
                  Grievance Registry
                </Link>
                <Link
                  to="/admin/departments"
                  className={`nav-btn ${isActive('/admin/departments') ? 'active' : ''}`}
                >
                  <Building size={16} />
                  Departments
                </Link>
                <Link
                  to="/admin/users"
                  className={`nav-btn ${isActive('/admin/users') ? 'active' : ''}`}
                >
                  <Users size={16} />
                  Users
                </Link>
                <Link
                  to="/admin/analytics"
                  className={`nav-btn ${isActive('/admin/analytics') ? 'active' : ''}`}
                >
                  <BarChart3 size={16} />
                  Analytics
                </Link>
                <Link
                  to="/admin/audit-logs"
                  className={`nav-btn ${isActive('/admin/audit-logs') ? 'active' : ''}`}
                >
                  <FileText size={16} />
                  Audit Logs
                </Link>
              </>
            )}

            {/* Officer Nav */}
            {isOfficer && (
              <>
                <Link
                  to="/officer/dashboard"
                  className={`nav-btn ${isActive('/officer/dashboard') ? 'active' : ''}`}
                >
                  <LayoutDashboard size={16} />
                  Dashboard
                </Link>
                <Link
                  to="/citizen/complaints"
                  className={`nav-btn ${isActive('/citizen/complaints') ? 'active' : ''}`}
                >
                  <History size={16} />
                  Department Queue
                </Link>
                <Link
                  to="/statistics"
                  className={`nav-btn ${isActive('/statistics') ? 'active' : ''}`}
                >
                  <BarChart3 size={16} />
                  Analytics
                </Link>
              </>
            )}

            {/* Shared Profile */}
            <Link
              to="/profile"
              className={`nav-btn ${isActive('/profile') ? 'active' : ''}`}
            >
              <User size={16} />
              Profile
            </Link>
          </nav>

          {/* User Session & Logout Capsule */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '0.5rem', borderLeft: '1px solid rgba(255,255,255,0.2)' }}>
            <div style={{ textAlign: 'right', fontSize: '0.82rem' }}>
              <div style={{ fontWeight: 700, color: '#ffffff' }}>{user?.name}</div>
              <div style={{ fontSize: '0.7rem', color: '#93c5fd', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {role} {user?.department_name ? `• ${user.department_name}` : ''}
              </div>
            </div>
            <button
              className="btn btn-secondary"
              onClick={logout}
              style={{
                fontSize: '0.78rem',
                padding: '0.35rem 0.65rem',
                background: 'rgba(255,255,255,0.15)',
                color: '#ffffff',
                border: '1px solid rgba(255,255,255,0.25)',
              }}
              title="Logout of Civic Portal"
            >
              <LogOut size={14} />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <Routes>
          {/* Citizen Routes (Section 43) */}
          <Route
            path="/citizen/dashboard"
            element={
              <ProtectedRoute allowedRoles={['CITIZEN']}>
                <CitizenDashboard
                  onNavigateSubmit={() => navigate('/citizen/complaints/new')}
                  onSelectComplaint={(id) => navigate(`/citizen/complaints/${id}`)}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="/citizen/complaints"
            element={
              <ProtectedRoute allowedRoles={['CITIZEN', 'DEPARTMENT_OFFICER']}>
                <ComplaintHistory onSelectComplaint={(id) => navigate(isOfficer ? `/admin/complaints/${id}` : `/citizen/complaints/${id}`)} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/citizen/complaints/new"
            element={
              <ProtectedRoute allowedRoles={['CITIZEN']}>
                <ComplaintForm onComplaintSubmitted={(res) => navigate(`/citizen/complaints/${res.complaint_id}`)} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/citizen/complaints/:id"
            element={
              <ProtectedRoute allowedRoles={['CITIZEN', 'DEPARTMENT_OFFICER', 'ADMIN']}>
                <ComplaintDetailsRoute defaultBack="/citizen/complaints" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/citizen/notifications"
            element={
              <ProtectedRoute allowedRoles={['CITIZEN']}>
                <NotificationsView />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes (Section 43) */}
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AdminDashboard
                  onNavigate={(tab) => {
                    if (tab === 'departments') navigate('/admin/departments');
                    else if (tab === 'users') navigate('/admin/users');
                    else if (tab === 'audit-logs') navigate('/admin/audit-logs');
                    else if (tab === 'statistics') navigate('/admin/analytics');
                    else navigate('/admin/complaints');
                  }}
                  onSelectComplaint={(id) => navigate(`/admin/complaints/${id}`)}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/complaints"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <ComplaintHistory onSelectComplaint={(id) => navigate(`/admin/complaints/${id}`)} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/complaints/:id"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <ComplaintDetailsRoute defaultBack="/admin/complaints" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/departments"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <DepartmentManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <UserManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/audit-logs"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AuditLogViewer />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/analytics"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <Statistics />
              </ProtectedRoute>
            }
          />

          {/* Officer Dashboard */}
          <Route
            path="/officer/dashboard"
            element={
              <ProtectedRoute allowedRoles={['DEPARTMENT_OFFICER']}>
                <OfficerDashboard onSelectComplaint={(id) => navigate(`/citizen/complaints/${id}`)} />
              </ProtectedRoute>
            }
          />

          {/* Shared Profile & Analytics */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/statistics"
            element={
              <ProtectedRoute>
                <Statistics />
              </ProtectedRoute>
            }
          />

          {/* Default Fallback Redirect */}
          <Route path="*" element={<HomeRedirect />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="footer-bar">
        <div className="footer-inner">
          <p>
            <strong>CivicResolve</strong> — Smart Complaints. Clear Decisions. Better Governance
          </p>
          <p style={{ opacity: 0.8, fontSize: '0.75rem' }}>
            Built with Pure Python Forward Chaining Engine &bull; Constraint Satisfaction Problem Solver &bull; FastAPI Backend &bull; SQLite Persistence &bull; React &amp; Vite UI &bull; Strict Role-Based Access Control
          </p>
        </div>
      </footer>
    </div>
  );
}

// Redirection handler for home or unrecognized paths
function HomeRedirect() {
  const { isAuthenticated, role, loading } = useAuth();

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
  if (role === 'DEPARTMENT_OFFICER') return <Navigate to="/officer/dashboard" replace />;
  return <Navigate to="/citizen/dashboard" replace />;
}

// Authentication Screen Wrapper
function AuthRoute({ mode }) {
  const { isAuthenticated, role } = useAuth();
  const navigate = useNavigate();

  if (isAuthenticated) {
    if (role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
    if (role === 'DEPARTMENT_OFFICER') return <Navigate to="/officer/dashboard" replace />;
    return <Navigate to="/citizen/dashboard" replace />;
  }

  if (mode === 'register') {
    return <Register onNavigateLogin={() => navigate('/login')} />;
  }
  if (mode === 'forgot-password') {
    return <ForgotPassword onNavigateLogin={() => navigate('/login')} />;
  }
  return (
    <Login
      onNavigateRegister={() => navigate('/register')}
      onNavigateForgotPassword={() => navigate('/forgot-password')}
    />
  );
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc', padding: '2rem' }}>
          <div className="card" style={{ maxWidth: 540, width: '100%', textAlign: 'center', padding: '2.5rem' }}>
            <div style={{ display: 'inline-flex', padding: '1rem', background: '#fee2e2', borderRadius: '50%', color: '#dc2626', marginBottom: '1.25rem' }}>
              <Shield size={36} />
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
              Application Recovery Interface
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              A client interface error occurred. You can return to the login screen or reload your session.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button
                className="btn btn-primary"
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.href = '/login';
                }}
              >
                Return to Login
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => window.location.reload()}
              >
                Reload Window
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<AuthRoute mode="login" />} />
            <Route path="/register" element={<AuthRoute mode="register" />} />
            <Route path="/forgot-password" element={<AuthRoute mode="forgot-password" />} />
            <Route path="/*" element={<MainLayout />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}
