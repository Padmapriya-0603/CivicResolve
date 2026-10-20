-- ============================================================
-- MySQL Database Schema: AI-Based Public Grievance Management System
-- Fulfills Sections 3, 5, 15, 29, 33, 34, 35, 36, 37, 38
-- ============================================================

CREATE DATABASE IF NOT EXISTS grievance_db;
USE grievance_db;

-- 1. Departments table (Section 36)
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    supported_issues JSON NOT NULL,
    escalation_authority VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Categories table (Section 7)
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Issue Types table
CREATE TABLE IF NOT EXISTS issue_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_type_id VARCHAR(50) UNIQUE NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    default_department_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (category_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Rules table (Section 35)
CREATE TABLE IF NOT EXISTS rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_id VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(150) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- ROUTING, PRIORITY, ESCALATION, CONFLICT
    description TEXT NOT NULL,
    conditions_json JSON NOT NULL,
    conclusion_json JSON NOT NULL,
    priority_order INT NOT NULL DEFAULT 10,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Users table (Section 5)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(30),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('CITIZEN', 'ADMIN') NOT NULL,
    department_id VARCHAR(50) DEFAULT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Complaints table (Section 15, 16, 17)
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_number VARCHAR(50) UNIQUE NOT NULL,
    complaint_id VARCHAR(50) UNIQUE NOT NULL,
    citizen_id INT DEFAULT NULL,
    citizen_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(150) NOT NULL,
    ward VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    location_type VARCHAR(100) DEFAULT 'Public Road',
    preferred_contact VARCHAR(30) DEFAULT 'Phone',
    category VARCHAR(100) NOT NULL,
    category_id VARCHAR(50) DEFAULT NULL,
    problem_type VARCHAR(100) NOT NULL,
    duration_days INT DEFAULT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
    immediate_danger ENUM('YES', 'NO') DEFAULT 'NO',
    affected_people VARCHAR(50) DEFAULT 'SINGLE',
    description TEXT,
    evidence_available BOOLEAN NOT NULL DEFAULT FALSE,
    evidence_filename VARCHAR(255) DEFAULT NULL,
    safety_risk ENUM('NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'NONE',
    public_accessibility_affected BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence BOOLEAN NOT NULL DEFAULT FALSE,
    emergency BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- AI vs Admin Decisions (Section 14 & 15)
    department VARCHAR(100) DEFAULT NULL,
    department_id VARCHAR(50) DEFAULT NULL,
    ai_department VARCHAR(100) DEFAULT NULL,
    ai_department_id VARCHAR(50) DEFAULT NULL,
    admin_department_id VARCHAR(50) DEFAULT NULL,
    ai_priority VARCHAR(30) DEFAULT NULL,
    final_priority VARCHAR(30) DEFAULT NULL,
    ai_escalation VARCHAR(30) DEFAULT NULL,
    final_escalation VARCHAR(30) DEFAULT NULL,
    priority VARCHAR(30) NOT NULL DEFAULT 'MEDIUM',
    escalation VARCHAR(30) NOT NULL DEFAULT 'NOT_REQUIRED',
    status ENUM('SUBMITTED', 'ACKNOWLEDGED', 'ACCEPTED', 'IN_PROGRESS', 'WORK_COMPLETED', 'USER_INFORMED', 'CLOSED') NOT NULL DEFAULT 'SUBMITTED',
    
    -- Manual Admin Override (Section 39)
    manual_override BOOLEAN NOT NULL DEFAULT FALSE,
    manual_department VARCHAR(100) DEFAULT NULL,
    manual_override_reason TEXT DEFAULT NULL,
    overridden_by VARCHAR(100) DEFAULT NULL,
    override_timestamp TIMESTAMP NULL DEFAULT NULL,
    
    -- Admin Messages & Milestones (Sections 20-25)
    admin_message TEXT DEFAULT NULL,
    work_started_message TEXT DEFAULT NULL,
    completion_message TEXT DEFAULT NULL,
    completed_by VARCHAR(100) DEFAULT NULL,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    notification_message TEXT DEFAULT NULL,
    informed_by VARCHAR(100) DEFAULT NULL,
    informed_at TIMESTAMP NULL DEFAULT NULL,
    closure_message TEXT DEFAULT NULL,
    closed_by VARCHAR(100) DEFAULT NULL,
    closed_at TIMESTAMP NULL DEFAULT NULL,
    
    -- Auditable structured reasoning info
    missing_info_json JSON DEFAULT NULL,
    conflicts_json JSON DEFAULT NULL,
    explanation TEXT DEFAULT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (citizen_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Complaint Timeline table (Section 29)
CREATE TABLE IF NOT EXISTS complaint_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    message_type ENUM('ACKNOWLEDGEMENT', 'ACCEPTANCE', 'PROGRESS_UPDATE', 'COMPLETION', 'FINAL_RESPONSE', 'CLOSURE', 'SYSTEM') NOT NULL DEFAULT 'SYSTEM',
    action_by VARCHAR(100) NOT NULL,
    action_by_role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Complaint Messages table (Section 33)
CREATE TABLE IF NOT EXISTS complaint_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(50) NOT NULL,
    admin_id INT DEFAULT NULL,
    message TEXT NOT NULL,
    message_type ENUM('ACKNOWLEDGEMENT', 'ACCEPTANCE', 'PROGRESS_UPDATE', 'COMPLETION', 'FINAL_RESPONSE', 'CLOSURE') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Notifications table (Section 34)
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    complaint_id VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Complaint Reasoning History table (Section 37)
CREATE TABLE IF NOT EXISTS complaint_reasoning (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(50) UNIQUE NOT NULL,
    input_facts JSON NOT NULL,
    constraints_checked JSON NOT NULL,
    CSP_result JSON NOT NULL,
    rules_evaluated JSON NOT NULL,
    rules_fired JSON NOT NULL,
    derived_facts JSON NOT NULL,
    final_conclusions JSON NOT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Reasoning Traces table (Section 12)
CREATE TABLE IF NOT EXISTS reasoning_traces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(50) NOT NULL,
    step_order INT NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    rule_id VARCHAR(50) DEFAULT NULL,
    rule_name VARCHAR(150) DEFAULT NULL,
    conditions_evaluated_json JSON DEFAULT NULL,
    derived_fact_json JSON DEFAULT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Audit Logs table (Section 38)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    user_email VARCHAR(150) DEFAULT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) DEFAULT NULL,
    old_value TEXT DEFAULT NULL,
    new_value TEXT DEFAULT NULL,
    reason TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
