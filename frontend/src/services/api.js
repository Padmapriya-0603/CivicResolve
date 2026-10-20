import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor to attach Bearer token to all outgoing requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('grievance_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Response interceptor to clear session on 401 Unauthorized across windows
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('grievance_token');
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new Event('storage'));
        if ('BroadcastChannel' in window) {
          const bc = new BroadcastChannel('grievance_auth_sync');
          bc.postMessage({ type: 'LOGOUT' });
          bc.close();
        }
      }
    }
    return Promise.reject(error);
  }
);


export const api = {
  // Health
  getHealth: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Auth
  register: async (userData) => {
    const res = await apiClient.post('/auth/register', userData);
    return res.data;
  },

  login: async (credentials) => {
    const res = await apiClient.post('/auth/login', credentials);
    return res.data;
  },

  forgotPassword: async (email) => {
    const res = await apiClient.post('/auth/forgot-password', { email });
    return res.data;
  },

  resetPassword: async (email, reset_code, new_password) => {
    const res = await apiClient.post('/auth/reset-password', { email, reset_code, new_password });
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  updateProfile: async (profileData) => {
    const res = await apiClient.put('/auth/profile', profileData);
    return res.data;
  },

  // Dashboard Statistics (Scoped by role)
  getDashboard: async () => {
    const res = await apiClient.get('/dashboard');
    return res.data;
  },

  // Complaints (Scoped by role)
  getComplaints: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.department) params.append('department', filters.department);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const res = await apiClient.get(`/complaints?${params.toString()}`);
    return res.data;
  },

  getComplaintById: async (id) => {
    const res = await apiClient.get(`/complaints/${encodeURIComponent(id)}`);
    return res.data;
  },

  submitComplaint: async (complaintData) => {
    const res = await apiClient.post('/complaints', complaintData);
    return res.data;
  },

  updateComplaintStatus: async (id, statusData) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/status`, statusData);
    return res.data;
  },

  overrideDepartment: async (id, overrideData) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/department`, overrideData);
    return res.data;
  },

  assignComplaint: async (id, assignData) => {
    const res = await apiClient.put(`/admin/complaints/${encodeURIComponent(id)}/assign`, assignData);
    return res.data;
  },

  // 5-Stage Grievance Lifecycle Actions
  acknowledgeComplaint: async (id, notes) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/acknowledge`, { notes });
    return res.data;
  },

  acceptComplaint: async (id, data) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/accept`, data);
    return res.data;
  },

  startWork: async (id, message) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/start-work`, { message });
    return res.data;
  },

  addProgressUpdate: async (id, message) => {
    const res = await apiClient.post(`/complaints/${encodeURIComponent(id)}/progress-update`, { message });
    return res.data;
  },

  completeWork: async (id, completion_message) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/complete-work`, { completion_message });
    return res.data;
  },

  informUser: async (id, notification_message) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/inform-user`, { notification_message });
    return res.data;
  },

  closeComplaint: async (id, closure_message) => {
    const res = await apiClient.put(`/complaints/${encodeURIComponent(id)}/close`, { closure_message });
    return res.data;
  },

  getTimeline: async (id) => {
    const res = await apiClient.get(`/complaints/${encodeURIComponent(id)}/timeline`);
    return res.data;
  },

  // Notifications (Section 89)
  getNotifications: async () => {
    const res = await apiClient.get('/notifications');
    return res.data;
  },

  markNotificationRead: async (id) => {
    const res = await apiClient.put(`/notifications/${encodeURIComponent(id)}/read`);
    return res.data;
  },

  markAllNotificationsRead: async () => {
    const res = await apiClient.put('/notifications/read-all');
    return res.data;
  },

  getReasoningTrace: async (id) => {
    const res = await apiClient.get(`/complaints/${encodeURIComponent(id)}/reasoning`);
    return res.data;
  },

  // Validation
  validateComplaint: async (data) => {
    const res = await apiClient.post('/validate-complaint', data);
    return res.data;
  },

  // Knowledge Base & Rules
  getRules: async () => {
    const res = await apiClient.get('/rules');
    return res.data;
  },

  toggleRule: async (ruleId) => {
    const res = await apiClient.put(`/rules/${encodeURIComponent(ruleId)}/toggle`);
    return res.data;
  },

  getDepartments: async () => {
    const res = await apiClient.get('/departments');
    return res.data;
  },

  createDepartment: async (deptData) => {
    const res = await apiClient.post('/departments', deptData);
    return res.data;
  },

  updateDepartment: async (deptId, deptData) => {
    const res = await apiClient.put(`/departments/${encodeURIComponent(deptId)}`, deptData);
    return res.data;
  },

  getCategories: async () => {
    const res = await apiClient.get('/categories');
    return res.data;
  },

  getIssueTypesForCategory: async (category) => {
    const res = await apiClient.get(`/issue-types/${encodeURIComponent(category)}`);
    return res.data;
  },

  getKnowledgeBase: async () => {
    const res = await apiClient.get('/knowledge-base');
    return res.data;
  },

  getMunicipalZones: async () => {
    const res = await apiClient.get('/municipal-zones');
    return res.data;
  },

  getWardsForZone: async (zoneId) => {
    const res = await apiClient.get(`/municipal-zones/${encodeURIComponent(zoneId)}/wards`);
    return res.data;
  },

  // Admin User Management
  getUsers: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.role) params.append('role', filters.role);
    if (filters.department_id) params.append('department_id', filters.department_id);
    if (filters.search) params.append('search', filters.search);

    const res = await apiClient.get(`/admin/users?${params.toString()}`);
    return res.data;
  },

  createUser: async (userData) => {
    const res = await apiClient.post('/admin/users', userData);
    return res.data;
  },

  updateUserStatus: async (userId, isActive) => {
    const res = await apiClient.put(`/admin/users/${userId}/status`, { is_active: isActive });
    return res.data;
  },

  updateUserRole: async (userId, role, departmentId = null) => {
    const res = await apiClient.put(`/admin/users/${userId}/role`, { role, department_id: departmentId });
    return res.data;
  },

  // Admin Audit Logs
  getAuditLogs: async (limit = 200) => {
    const res = await apiClient.get(`/admin/audit-logs?limit=${limit}`);
    return res.data;
  },

  // Evidence upload & retrieval
  uploadEvidence: async (file) => {
    const token = localStorage.getItem('grievance_token');
    const formData = new FormData();
    formData.append('file', file);
    const res = await axios.post(`${API_BASE_URL}/evidence-upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': token ? `Bearer ${token}` : '',
      },
    });
    return res.data;
  },

  getEvidenceUrl: (filename) => {
    if (!filename) return '';
    return `${API_BASE_URL}/evidence/${encodeURIComponent(filename)}`;
  },
};

export default api;
