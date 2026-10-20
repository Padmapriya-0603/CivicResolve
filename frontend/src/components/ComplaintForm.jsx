import React, { useState, useEffect } from 'react';
import { Send, Upload, AlertCircle, Check, MapPin } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { CHENNAI_ZONES, getZoneByNameOrId, getWardsForZone } from '../data/chennaiZones';

const DEFAULT_FORM_STATE = {
  citizen_name: '',
  phone: '',
  email: '',
  zone: 'Zone 8 - Anna Nagar',
  ward: 'Ward 101 - Anna Nagar East',
  location: '',
  location_type: 'Public Road',
  preferred_contact: 'Phone',
  category: 'Public Lighting',
  issue_type: 'Streetlight Not Working',
  duration_days: 1,
  severity: 'MEDIUM',
  immediate_danger: 'NO',
  affected_people_type: 'Multiple',
  affected_people: 10,
  description: '',
  frequency: 'OCCASIONAL',
  evidence_available: false,
  evidence_filename: '',
  safety_risk: 'LOW',
  public_accessibility_affected: false,
  recurrence: false,
  emergency: false,
};

export default function ComplaintForm({ onComplaintSubmitted }) {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    ...DEFAULT_FORM_STATE,
    citizen_name: user?.name || '',
    phone: user?.phone || '',
    email: user?.email || '',
  });
  const [categories, setCategories] = useState([]);
  const [issueTypes, setIssueTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [validationErrors, setValidationErrors] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [filePreviewUrl, setFilePreviewUrl] = useState(null);
  const [isPdf, setIsPdf] = useState(false);
  const [liveCspStatus, setLiveCspStatus] = useState({ checked: false, valid: true, violations: [] });

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        citizen_name: prev.citizen_name || user.name || '',
        phone: prev.phone || user.phone || '',
        email: prev.email || user.email || '',
      }));
    }
  }, [user]);

  // Fetch categories on load
  useEffect(() => {
    async function loadTaxonomy() {
      try {
        const cats = await api.getCategories();
        setCategories(cats);
        if (cats.length > 0) {
          const firstCat = cats.find(c => c.name === 'Public Lighting') || cats[0];
          loadIssuesForCategory(firstCat.name);
        }
      } catch (err) {
        console.error('Failed to load categories', err);
      }
    }
    loadTaxonomy();
  }, []);

  const loadIssuesForCategory = async (catName) => {
    try {
      const issues = await api.getIssueTypesForCategory(catName);
      setIssueTypes(issues);
      if (issues.length > 0) {
        setFormData(prev => ({
          ...prev,
          category: catName,
          issue_type: issues[0].name
        }));
      }
    } catch (err) {
      console.error('Failed to load issues for category', err);
    }
  };

  const handleCategoryChange = (e) => {
    const selectedCat = e.target.value;
    loadIssuesForCategory(selectedCat);
  };

  const handleZoneChange = (e) => {
    const selectedZone = e.target.value;
    const availableWards = getWardsForZone(selectedZone);
    setFormData(prev => ({
      ...prev,
      zone: selectedZone,
      ward: availableWards.length > 0 ? availableWards[0].name : ''
    }));
  };

  const currentZoneObj = getZoneByNameOrId(formData.zone);
  const availableWards = currentZoneObj ? currentZoneObj.wards : [];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => {
      const next = {
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      };
      // Keep immediate_danger and emergency aligned if user toggles emergency
      if (name === 'emergency') {
        next.immediate_danger = checked ? 'YES' : next.immediate_danger;
      }
      if (name === 'immediate_danger' && value === 'YES') {
        next.emergency = true;
      }
      return next;
    });
  };

  // Real-time CSP validation check
  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const validation = await api.validateComplaint({
          category: formData.category,
          issue_type: formData.issue_type,
          duration_days: Number(formData.duration_days || 0),
          affected_people: Number(formData.affected_people || 1),
          severity: formData.severity,
          safety_risk: formData.safety_risk,
          emergency: formData.emergency || formData.immediate_danger === 'YES',
          frequency: formData.frequency,
        });
        setLiveCspStatus({
          checked: true,
          valid: validation.valid,
          violations: validation.violations || []
        });
      } catch (err) {
        // Silently skip if network blips during typing
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [formData.category, formData.issue_type, formData.duration_days, formData.affected_people, formData.severity, formData.safety_risk, formData.emergency, formData.immediate_danger, formData.frequency]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const isPdfDoc = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    setIsPdf(isPdfDoc);

    if (!isPdfDoc && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => setFilePreviewUrl(event.target.result);
      reader.readAsDataURL(file);
    } else {
      setFilePreviewUrl(null);
    }

    try {
      setUploadStatus('Uploading supporting evidence...');
      const res = await api.uploadEvidence(file);
      setFormData(prev => ({
        ...prev,
        evidence_available: true,
        evidence_filename: res.filename
      }));
      setUploadStatus(`Uploaded: ${res.filename} (Available for officer & admin review)`);
    } catch (err) {
      setUploadStatus(`Upload failed: ${err.response?.data?.detail || err.message}`);
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setValidationErrors([]);
    setLoading(true);

    try {
      // 1. Client-Side CSP validation call
      const validation = await api.validateComplaint({
        category: formData.category,
        issue_type: formData.issue_type,
        duration_days: Number(formData.duration_days),
        affected_people: Number(formData.affected_people),
        severity: formData.severity,
        safety_risk: formData.safety_risk,
        emergency: formData.emergency || formData.immediate_danger === 'YES',
        frequency: formData.frequency,
      });

      if (!validation.valid) {
        setValidationErrors(validation.violations);
        setLoading(false);
        return;
      }

      // 2. Submit Complaint to backend
      const payload = {
        ...formData,
        emergency: formData.emergency || formData.immediate_danger === 'YES',
        duration_days: formData.duration_days === '' ? null : Number(formData.duration_days),
        affected_people: formData.affected_people === '' ? null : Number(formData.affected_people),
      };

      const result = await api.submitComplaint(payload);
      onComplaintSubmitted(result);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || err.message || 'Submission failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <Send size={20} color="#1e3a8a" />
            Citizen Grievance Registration
          </h2>
          <p className="card-subtitle">
            Lodge your municipal grievance. Once submitted, the Municipal Administrator will review, accept, and assign it to the respective department for resolution.
          </p>
        </div>

      </div>

      {/* Real-Time CSP Inconsistency Banner (only shown if contradictions exist) */}
      {liveCspStatus.checked && !liveCspStatus.valid && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            marginBottom: '1.25rem',
            border: '1px solid #fca5a5',
            background: '#fef2f2',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertCircle size={20} color="#dc2626" />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#991b1b' }}>
                Constraint Inconsistency Detected
              </div>
              <div style={{ fontSize: '0.78rem', color: '#b91c1c' }}>
                {liveCspStatus.violations.join(' | ')}
              </div>
            </div>
          </div>
          <span
            className="badge"
            style={{
              background: '#dc2626',
              color: '#ffffff',
              fontSize: '0.75rem'
            }}
          >
            INCONSISTENCY
          </span>
        </div>
      )}

      {/* Validation / Error Alerts */}
      {errorMsg && (
        <div className="conflict-box blocking">
          <div className="conflict-title" style={{ color: '#991b1b' }}>
            <AlertCircle size={18} />
            Constraint Rejection
          </div>
          <p style={{ fontSize: '0.88rem' }}>{errorMsg}</p>
        </div>
      )}

      {validationErrors.length > 0 && (
        <div className="conflict-box blocking">
          <div className="conflict-title" style={{ color: '#991b1b' }}>
            <AlertCircle size={18} />
            CSP Constraint Violations ({validationErrors.length})
          </div>
          <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem' }}>
            {validationErrors.map((v, i) => (
              <li key={i}>{v}</li>
            ))}
          </ul>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Section 1: Citizen Information */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '0.75rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.3rem' }}>
          1. Citizen Identification &amp; Location
        </h4>
        <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">Citizen Name *</label>
            <input
              type="text"
              name="citizen_name"
              className="form-input"
              value={formData.citizen_name}
              onChange={handleChange}
              required
              placeholder="e.g. Ramesh Kumar"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Phone Number *</label>
            <input
              type="text"
              name="phone"
              className="form-input"
              value={formData.phone}
              onChange={handleChange}
              required
              placeholder="e.g. +91 98765 43210"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address *</label>
            <input
              type="email"
              name="email"
              className="form-input"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="e.g. citizen@example.com"
            />
          </div>

          {/* Municipal Zone & Ward Selectors (Chennai Corporation GCC) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <MapPin size={15} color="#1e3a8a" />
                Municipal Zone (Chennai GCC) *
              </label>
              <select
                name="zone"
                className="form-select"
                value={formData.zone}
                onChange={handleZoneChange}
                required
              >
                <option value="">— Select Municipal Zone (1 - 15) —</option>
                {CHENNAI_ZONES.map(z => (
                  <option key={z.id} value={z.name}>
                    {z.name} ({z.wards.length} Wards)
                  </option>
                ))}
              </select>
              {currentZoneObj && (
                <div style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '0.3rem' }}>
                  <strong>Key Localities:</strong> {currentZoneObj.description}
                </div>
              )}
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <MapPin size={15} color="#2563eb" />
                Municipal Ward (GCC 1 - 200) *
              </label>
              <select
                name="ward"
                className="form-select"
                value={formData.ward}
                onChange={handleChange}
                required
                disabled={!formData.zone}
              >
                {!formData.zone ? (
                  <option value="">— Select Zone first to choose Ward —</option>
                ) : (
                  <>
                    <option value="">— Select Municipal Ward —</option>
                    {availableWards.map(w => (
                      <option key={w.id} value={w.name}>
                        {w.name}
                      </option>
                    ))}
                  </>
                )}
              </select>
              {formData.zone && (
                <div style={{ fontSize: '0.74rem', color: '#16a34a', marginTop: '0.3rem', fontWeight: 500 }}>
                  ✓ {availableWards.length} municipal wards configured in {formData.zone.split(' - ')[1] || formData.zone}
                </div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Exact Location / Landmark *</label>
            <input
              type="text"
              name="location"
              className="form-input"
              value={formData.location}
              onChange={handleChange}
              required
              placeholder="e.g. Cross Junction 4, Main Street"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Location Type *</label>
            <select
              name="location_type"
              className="form-select"
              value={formData.location_type}
              onChange={handleChange}
            >
              <option value="Public Road">Public Road / Street</option>
              <option value="Residential Area">Residential Area</option>
              <option value="Commercial Area">Commercial Area / Market</option>
              <option value="Government Building">Government Building</option>
              <option value="Park/Recreational Area">Park / Recreational Area</option>
              <option value="School Zone">School Zone</option>
              <option value="Hospital Area">Hospital / Healthcare Area</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Preferred Contact Method</label>
            <select
              name="preferred_contact"
              className="form-select"
              value={formData.preferred_contact}
              onChange={handleChange}
            >
              <option value="Phone">Phone Call</option>
              <option value="Email">Email</option>
              <option value="SMS">SMS</option>
            </select>
          </div>
        </div>

        {/* Section 2: Category and Dependent Issue Type */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '0.75rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.3rem' }}>
          2. Grievance Classification (CSP Domain Dependent)
        </h4>
        <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">Grievance Category *</label>
            <select
              name="category"
              className="form-select"
              value={formData.category}
              onChange={handleCategoryChange}
              required
            >
              {categories.map((c) => (
                <option key={c.category_id} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Restricts issue types to consistent domain choices
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Specific Issue Type *</label>
            <select
              name="issue_type"
              className="form-select"
              value={formData.issue_type}
              onChange={handleChange}
              required
            >
              {issueTypes.map((it) => (
                <option key={it.issue_type_id} value={it.name}>
                  {it.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Section 3: Structured Severity, Risk, & Population Impact */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '0.75rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.3rem' }}>
          3. Quantifiable Impact, Danger &amp; Safety Attributes (CSP Constraints)
        </h4>
        <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">Duration of Grievance (Days)</label>
            <input
              type="number"
              min="0"
              name="duration_days"
              className="form-input"
              value={formData.duration_days}
              onChange={handleChange}
              placeholder="Days (e.g. 5)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Reported Severity *</label>
            <select
              name="severity"
              className="form-select"
              value={formData.severity}
              onChange={handleChange}
              required
            >
              <option value="LOW">LOW — Minor inconvenience</option>
              <option value="MEDIUM">MEDIUM — Noticeable civic impairment</option>
              <option value="HIGH">HIGH — Significant disruption</option>
              <option value="CRITICAL">CRITICAL — Severe structural/health hazard</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Immediate Danger Present? *</label>
            <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.4rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', fontWeight: 600 }}>
                <input
                  type="radio"
                  name="immediate_danger"
                  value="YES"
                  checked={formData.immediate_danger === 'YES'}
                  onChange={handleChange}
                />
                <span style={{ color: '#b91c1c' }}>YES (Threat to Life/Safety)</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="immediate_danger"
                  value="NO"
                  checked={formData.immediate_danger === 'NO'}
                  onChange={handleChange}
                />
                <span>NO</span>
              </label>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              CSP Constraint: Immediate danger prohibits LOW priority classification
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Affected Population Scope *</label>
            <div style={{ display: 'flex', gap: '1.25rem', marginBottom: '0.4rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="affected_people_type"
                  value="Single"
                  checked={formData.affected_people_type === 'Single'}
                  onChange={(e) => {
                    handleChange(e);
                    setFormData(prev => ({ ...prev, affected_people_type: 'Single', affected_people: 1 }));
                  }}
                />
                <span>Single (1 citizen)</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="affected_people_type"
                  value="Multiple"
                  checked={formData.affected_people_type === 'Multiple'}
                  onChange={(e) => {
                    handleChange(e);
                    if (formData.affected_people <= 1) {
                      setFormData(prev => ({ ...prev, affected_people_type: 'Multiple', affected_people: 10 }));
                    }
                  }}
                />
                <span>Multiple Citizens (&gt; 1)</span>
              </label>
            </div>
            <input
              type="number"
              min="1"
              name="affected_people"
              className="form-input"
              value={formData.affected_people}
              onChange={handleChange}
              placeholder="Estimated count (e.g. 80)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Occurrence Frequency *</label>
            <select
              name="frequency"
              className="form-select"
              value={formData.frequency}
              onChange={handleChange}
              required
            >
              <option value="ONE_TIME">ONE_TIME — Occurred once</option>
              <option value="OCCASIONAL">OCCASIONAL — Intermittent occurrence</option>
              <option value="FREQUENT">FREQUENT — Multiple times daily/weekly</option>
              <option value="CONTINUOUS">CONTINUOUS — Uninterrupted problem</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Safety Risk Level *</label>
            <select
              name="safety_risk"
              className="form-select"
              value={formData.safety_risk}
              onChange={handleChange}
              required
            >
              <option value="NONE">NONE — No safety hazard</option>
              <option value="LOW">LOW — Minor trip/nuisance risk</option>
              <option value="MEDIUM">MEDIUM — Moderate hazard</option>
              <option value="HIGH">HIGH — Dangerous condition</option>
              <option value="CRITICAL">CRITICAL — Imminent threat to life/limb</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Supporting Evidence File (Photo/PDF)</label>
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.webp,.pdf"
              className="form-input"
              onChange={handleFileUpload}
            />
            <small style={{ fontSize: '0.73rem', color: '#64748b', display: 'block', marginTop: '0.2rem' }}>
              Upload a clear photo (JPG, PNG, WEBP) or PDF document. Directly visible to inspecting Department Officers &amp; Admins.
            </small>

            {formData.evidence_filename && (
              <div style={{ marginTop: '0.6rem', padding: '0.65rem 0.85rem', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                  {filePreviewUrl ? (
                    <img src={filePreviewUrl} alt="Preview" style={{ width: '48px', height: '48px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #86efac' }} />
                  ) : (
                    <span style={{ fontSize: '1.6rem' }}>{isPdf ? '📄' : '📎'}</span>
                  )}
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#166534' }}>
                      {isPdf ? 'PDF Document Attached' : 'Photo Attached'}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: '#475569', wordBreak: 'break-all' }}>
                      {formData.evidence_filename}
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '0.25rem 0.55rem' }}
                  onClick={() => {
                    setFormData(prev => ({ ...prev, evidence_available: false, evidence_filename: '' }));
                    setFilePreviewUrl(null);
                    setUploadStatus('');
                  }}
                >
                  Remove
                </button>
              </div>
            )}

            {uploadStatus && !formData.evidence_filename && (
              <span style={{ fontSize: '0.75rem', color: '#0f766e', marginTop: '0.2rem', display: 'block' }}>
                {uploadStatus}
              </span>
            )}
          </div>
        </div>

        {/* Section 4: Grievance Description & Civic Conditions */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e3a8a', marginBottom: '0.75rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.3rem' }}>
          4. Grievance Particulars &amp; Special Civic Conditions
        </h4>
        <div className="form-group" style={{ marginBottom: '1.25rem' }}>
          <label className="form-label">Grievance Description / Context</label>
          <textarea
            name="description"
            className="form-input"
            rows="3"
            value={formData.description}
            onChange={handleChange}
            placeholder="Provide relevant facts, physical landmarks, or civic context for municipal inspectors..."
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <label className="form-checkbox-label">
            <input
              type="checkbox"
              name="public_accessibility_affected"
              checked={formData.public_accessibility_affected}
              onChange={handleChange}
            />
            <span>Public Transit / Road Access Impeded</span>
          </label>

          <label className="form-checkbox-label">
            <input
              type="checkbox"
              name="recurrence"
              checked={formData.recurrence}
              onChange={handleChange}
            />
            <span>Recurring Issue (Reported Previously)</span>
          </label>

          <label className="form-checkbox-label" style={{ color: (formData.emergency || formData.immediate_danger === 'YES') ? '#b91c1c' : 'inherit' }}>
            <input
              type="checkbox"
              name="emergency"
              checked={formData.emergency || formData.immediate_danger === 'YES'}
              onChange={handleChange}
            />
            <strong>Flag as Emergency Condition</strong>
          </label>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ minWidth: '180px' }}
          >
            {loading ? 'Submitting Grievance...' : 'Submit Grievance'}
          </button>
        </div>
      </form>
    </div>
  );
}
