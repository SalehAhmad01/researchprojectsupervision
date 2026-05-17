# Software Requirements Specification

# Research Project Supervision Management System

## Document Control

- **Document Type:** Software Requirements Specification
- **System Name:** Research Project Supervision Management System
- **Technology Stack:** Django 6.x, Python, SQLite, Bootstrap-based templates
- **Prepared For:** Academic research project supervision environment
- **Prepared By:** Codebase Analysis and System Architecture Review
- **Version:** 1.0

## Table of Contents

1. Introduction
2. System Overview
3. Stakeholders and User Classes
4. Existing System Architecture
5. Functional Requirements
6. Non-Functional Requirements
7. System Modelling
8. Data Model Specification
9. Security Requirements and Controls
10. Business Rules
11. User Interface Requirements
12. External Interfaces
13. Testing Methodology
14. Deployment and Configuration Requirements
15. Traceability Matrix
16. Assumptions, Constraints, and Future Enhancements

---

# 1. Introduction

## 1.1 Purpose

This Software Requirements Specification documents the requirements, architecture, system behaviour, security model, and testing approach for the Research Project Supervision Management System. The system is a Django-based enterprise-style web application designed to manage academic research supervision workflows including user management, topic submission, supervisor assignment, draft submission, feedback, notifications, dashboards, and audit logging.

## 1.2 Scope

The system supports three primary user roles:

- **Student:** submits research topics and uploads chapter drafts.
- **Supervisor:** reviews drafts and provides feedback.
- **Coordinator:** manages students and supervisors, approves topics, assigns supervisors, performs bulk user uploads, and monitors system progress.

The application provides centralized supervision workflow management for academic departments and reduces manual coordination overhead through role-based dashboards, CSV-based user onboarding, bulk assignment, notifications, and audit logs.

## 1.3 Product Perspective

The system is implemented as a modular Django web application with the following internal apps:

- **accounts:** authentication, custom user model, role validation, profile management, bulk user management.
- **projects:** research topics, project status workflow, supervisor assignments.
- **drafts:** chapter draft uploads, versioning, file validation, file hashing.
- **feedbacks:** supervisor feedback, review decisions, progress scoring.
- **dashboard:** role-specific dashboards and analytics.
- **notifications:** in-system user notifications.
- **audit:** request-level activity logging for mutating operations.

## 1.4 Definitions and Acronyms

- **SRS:** Software Requirements Specification.
- **RBAC:** Role-Based Access Control.
- **CSV:** Comma-Separated Values.
- **CRUD:** Create, Read, Update, Delete.
- **CSRF:** Cross-Site Request Forgery.
- **PII:** Personally Identifiable Information.
- **UAT:** User Acceptance Testing.

---

# 2. System Overview

## 2.1 Enterprise Problem

Academic institutions need a controlled platform to manage the research supervision process. Manual processes are error-prone, difficult to audit, and inefficient when handling large cohorts of students and supervisors. Coordinators require bulk onboarding and assignment features, supervisors need structured feedback channels, and students need a transparent way to submit topics and drafts.

## 2.2 System Objectives

The system shall:

- Provide role-based access for students, supervisors, and coordinators.
- Allow students to submit research topics.
- Allow coordinators to approve projects and assign supervisors.
- Allow coordinators to upload eligible students and supervisors in bulk using CSV.
- Allow coordinators to create individual student and supervisor accounts.
- Allow coordinators to assign students/projects to supervisors in bulk.
- Allow students to upload chapter drafts with version tracking.
- Allow supervisors to review drafts and provide feedback.
- Notify relevant users about workflow events.
- Maintain audit logs for state-changing requests.

## 2.3 High-Level Workflow

1. User registers or is created by coordinator.
2. User logs in through a role-specific login path.
3. Student submits a research topic.
4. Coordinator reviews project submissions.
5. Coordinator assigns a supervisor manually or through bulk assignment.
6. Student uploads chapter drafts.
7. Supervisor reviews drafts and submits feedback.
8. Student and coordinator track progress through dashboards.
9. Mutating actions are recorded in audit logs.

---

# 3. Stakeholders and User Classes

## 3.1 Student

Students are academic users who submit research topics and upload chapter drafts. They can view their own projects, drafts, feedback, and progress.

## 3.2 Supervisor

Supervisors are academic staff responsible for supervising assigned student projects. They can view assigned projects, review draft submissions, and provide feedback decisions.

## 3.3 Coordinator

Coordinators are administrative academic users responsible for managing supervision workflows. They can manage users, approve projects, assign supervisors, monitor dashboards, and perform bulk operations.

## 3.4 System Administrator

System administrators access Django admin functionality and can manage system data at an administrative level. Staff users may also be treated as coordinators by the custom user model logic.

---

# 4. Existing System Architecture

## 4.1 Architectural Style

The system follows Django's Model-Template-View architecture:

- **Models:** define database schema and domain entities.
- **Views:** implement request handling and business workflows.
- **Templates:** render user interfaces.
- **Forms:** validate user input and file uploads.
- **Services:** provide reusable operations such as notifications and conflict checks.
- **Middleware:** records activity logs for mutating HTTP requests.

## 4.2 Main Components

| Component | Responsibility |
|---|---|
| `accounts` | Authentication, custom users, roles, registration, profile, coordinator user management |
| `projects` | Research topic submission, status lifecycle, supervisor assignment |
| `drafts` | Chapter draft upload, versioning, file validation, hash generation |
| `feedbacks` | Feedback creation, decision recording, progress score validation |
| `dashboard` | Role-based dashboard routing and analytics |
| `notifications` | In-app notification creation and listing |
| `audit` | Activity logging middleware and audit records |
| `config` | Settings, URL routing, WSGI/ASGI configuration |

## 4.3 URL Structure

| URL Prefix | Purpose |
|---|---|
| `/admin/` | Django administration |
| `/accounts/` | Login, logout, registration, profile, user management |
| `/projects/` | Project list, creation, detail, approval, supervisor assignment |
| `/drafts/` | Draft list, upload, detail |
| `/feedbacks/` | Feedback creation and listing |
| `/notifications/` | User notifications |
| `/` | Dashboard redirect and role dashboards |

## 4.4 Dependency Stack

The project currently depends on:

- **Django >= 6.0, < 6.1**
- **python-decouple 3.8** for environment-based configuration
- **Pillow** for image-related compatibility
- **qrcode 7.4.2** for QR-code functionality if required by the system

---

# 5. Functional Requirements

## 5.1 Authentication and Role-Based Login

### FR-001: Role-Based Login

The system shall provide login access for students, supervisors, and coordinators.

- **Input:** username, password, selected role.
- **Processing:** selected role is validated against the authenticated user's stored role.
- **Output:** successful login redirects user to the appropriate dashboard.
- **Security:** users cannot log in through an incorrect role path.

### FR-002: Registration

The system shall allow user registration with role-specific validation.

- Students must provide a student ID.
- Supervisors and coordinators must provide a staff ID.
- Student accounts must not store staff ID.
- Staff accounts must not store student ID.

### FR-003: Profile Management

Authenticated users shall be able to update their own profile fields including names, email, department, IDs, and phone.

## 5.2 Coordinator User Management

### FR-004: Bulk User Upload

The coordinator shall upload student and supervisor accounts through CSV.

Required columns:

```csv
username,email,role
```

Optional columns:

```csv
first_name,last_name,department,student_id,staff_id,phone,password,eligible
```

Processing rules:

- Existing usernames are updated.
- New usernames are created.
- Only `student` and `supervisor` roles are allowed.
- Coordinator accounts are not created through bulk upload.
- CSV files must have `.csv` extension.
- CSV file size must not exceed 2MB.
- Student rows may set `eligible=true` to mark students eligible for assignment.
- Supervisor rows store department information for assignment planning.

### FR-005: Single User Creation

The coordinator shall manually create one student or supervisor account through a Single User tab.

Rules:

- Role must be student or supervisor.
- Student ID is required for student users.
- Staff ID is required for supervisor users.
- Password is optional; if omitted, an unusable password is assigned.

### FR-006: Bulk Assignment

The coordinator shall assign eligible students/projects to supervisors through CSV.

Required columns:

```csv
student_username,supervisor_username
```

Optional columns:

```csv
project_title,notes
```

Rules:

- Student must exist and be eligible.
- Supervisor must exist and be active.
- If `project_title` is provided, the matching student project is assigned.
- If `project_title` is empty, the latest student project is assigned.
- Assignment creates or updates a `SupervisorAssignment` record.
- Project supervisor is updated.
- Project coordinator is set to the current coordinator.
- Project status is set to `Under Review`.

## 5.3 Project Management

### FR-007: Topic Submission

Students shall submit research topics with project title, abstract, and keywords.

### FR-008: Project Listing

The system shall display project lists according to role:

- Student sees own projects.
- Supervisor sees assigned projects.
- Coordinator sees all projects.

### FR-009: Project Detail

Authenticated users shall view project details according to accessible project querysets.

### FR-010: Project Approval

Coordinator shall approve submitted projects. Approval sets:

- Project status to `Approved`.
- Coordinator to approving user.
- Approval date to current timestamp.

### FR-011: Manual Supervisor Assignment

Coordinator shall assign a supervisor to a project through a dedicated page.

Rules:

- Assignment links a project to one supervisor.
- Project status changes to `Under Review`.
- Supervisor is notified.
- Department conflict warning may be displayed.

## 5.4 Draft Submission

### FR-012: Draft Upload

Students shall upload chapter drafts for their projects.

Rules:

- Allowed file types: PDF, DOC, DOCX.
- Maximum file size: 5MB.
- Drafts are versioned by project and chapter.
- File hash is generated using SHA-256.
- Supervisor is notified when a draft is uploaded.

### FR-013: Draft Listing

The system shall list drafts by role:

- Student sees own project drafts.
- Supervisor sees drafts for assigned projects.
- Coordinator sees all drafts.

## 5.5 Feedback Management

### FR-014: Feedback Creation

Supervisor shall provide feedback for drafts assigned to them.

Feedback includes:

- Decision: approved, rejected, revision required.
- Comments.
- Progress score from 0 to 100.

Rules:

- Supervisor can only provide feedback on drafts for assigned projects.
- Draft status is updated to match feedback decision.
- Student receives a notification.

## 5.6 Notifications

### FR-015: Notification Creation

The system shall create notifications for major workflow events including:

- New supervision assignment.
- Topic approval.
- New draft submission.
- Draft feedback received.

### FR-016: Notification Read State

Notifications shall support read/unread status.

## 5.7 Dashboard and Analytics

### FR-017: Dashboard Redirect

Authenticated users shall be redirected to role-specific dashboards.

### FR-018: Student Dashboard

Student dashboard shall show project progress based on draft count.

### FR-019: Supervisor Dashboard

Supervisor dashboard shall show assigned projects and pending draft submissions.

### FR-020: Coordinator Dashboard

Coordinator dashboard shall show:

- Total projects.
- Pending approvals.
- Supervisor workload.
- Project status counts.
- Delayed submissions count.

## 5.8 Audit Logging

### FR-021: Activity Logging

The system shall log authenticated POST, PUT, PATCH, and DELETE requests.

Captured fields:

- Actor.
- Action.
- Path.
- HTTP method.
- IP address.
- User agent.
- Timestamp.

---

# 6. Non-Functional Requirements

## 6.1 Security

- The system shall enforce authentication for protected resources.
- The system shall enforce role-based access control for role-specific actions.
- The system shall use Django CSRF middleware for form submissions.
- The system shall use Django password hashing.
- The system shall validate uploaded file types and sizes.
- The system shall avoid hardcoded production secrets through environment variables.

## 6.2 Performance

- Common querysets shall use `select_related` and `prefetch_related` where appropriate.
- Dashboard analytics shall use database aggregation for counts.
- CSV upload size is limited to 2MB to prevent excessive request processing.
- Draft upload size is limited to 5MB.

## 6.3 Reliability

- Model constraints enforce unique draft versions per project and chapter.
- Unique student and staff IDs reduce duplicate identity records.
- Supervisor assignments use one-to-one relation with projects to prevent multiple active supervisors for one project assignment record.

## 6.4 Maintainability

- The codebase is separated into domain-specific Django apps.
- Forms centralize input validation.
- Mixins centralize role-based access logic.
- Services isolate notification creation and conflict detection logic.

## 6.5 Usability

- Role-based login provides clear entry points.
- Coordinator user management uses tabs for bulk upload, single user creation, and bulk assignment.
- Templates use styled cards and guidance panels to improve workflow clarity.

## 6.6 Auditability

- Mutating authenticated requests are recorded in `ActivityLog`.
- Feedback, assignments, drafts, and notifications contain timestamp fields.

---

# 7. System Modelling

## 7.1 Context Model

```text
+------------------+        +------------------------------------------+
| Student          | -----> | Research Project Supervision System       |
+------------------+        |                                          |
| Supervisor       | -----> | - Accounts and Authentication             |
+------------------+        | - Project Management                      |
| Coordinator      | -----> | - Draft Submission                        |
+------------------+        | - Feedback                                |
| Admin            | -----> | - Notifications                           |
+------------------+        | - Audit Logging                           |
                            +--------------------+---------------------+
                                                 |
                                                 v
                                      +--------------------+
                                      | SQLite Database    |
                                      +--------------------+
```

## 7.2 Use Case Model

### Student Use Cases

- Register and log in as student.
- Submit research topic.
- View own project list.
- Upload chapter draft.
- View supervisor feedback.
- Track progress from dashboard.

### Supervisor Use Cases

- Log in as supervisor.
- View assigned projects.
- View submitted drafts.
- Submit feedback and progress scores.
- Monitor pending drafts.

### Coordinator Use Cases

- Log in as coordinator.
- Upload eligible students using CSV.
- Upload supervisors with department data using CSV.
- Create single student or supervisor account.
- Assign supervisors manually.
- Assign students/projects to supervisors in bulk.
- Approve research topics.
- View coordinator analytics dashboard.

## 7.3 Activity Model: Bulk User Upload

```text
Coordinator selects Bulk Upload
        |
        v
Uploads CSV file
        |
        v
Validate extension and size
        |
        v
Validate required columns
        |
        v
For each row:
  - Validate username, email, role
  - Normalize department and ID fields
  - Mark eligible if applicable
  - Create or update user
        |
        v
Display created, updated, skipped counts
```

## 7.4 Activity Model: Bulk Assignment

```text
Coordinator selects Bulk Assignments
        |
        v
Uploads assignment CSV
        |
        v
Validate required columns
        |
        v
For each row:
  - Find eligible student
  - Find active supervisor
  - Find matching or latest project
  - Create/update supervisor assignment
  - Update project supervisor, coordinator, status
        |
        v
Display assigned and skipped counts
```

## 7.5 Project State Model

```text
Submitted
   |
   | coordinator assigns supervisor
   v
Under Review
   |
   | coordinator approves
   v
Approved
   |
   | future completion process
   v
Completed

Rejected may be used for declined topics or future rejection workflows.
```

## 7.6 Draft State Model

```text
Submitted
   |
   | supervisor feedback
   +--> Approved
   +--> Rejected
   +--> Revision Required
```

---

# 8. Data Model Specification

## 8.1 User

The system uses a custom user model extending Django `AbstractUser`.

| Field | Type | Description |
|---|---|---|
| `role` | CharField | student, supervisor, coordinator |
| `department` | CharField | Academic department |
| `student_id` | CharField unique nullable | Student identity number |
| `staff_id` | CharField unique nullable | Staff identity number |
| `phone` | CharField | Contact number |
| `is_verified` | Boolean | Used as student eligibility flag |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

## 8.2 ResearchProject

| Field | Type | Description |
|---|---|---|
| `student` | FK User | Student owner |
| `title` | CharField | Research topic title |
| `abstract` | TextField | Research abstract |
| `keywords` | CharField | Optional keywords |
| `status` | CharField | submitted, under_review, approved, rejected, completed |
| `supervisor` | FK User nullable | Assigned supervisor |
| `coordinator` | FK User nullable | Responsible coordinator |
| `approval_date` | DateTime nullable | Approval timestamp |
| `deadline` | Date nullable | Optional project deadline |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

## 8.3 SupervisorAssignment

| Field | Type | Description |
|---|---|---|
| `project` | OneToOne ResearchProject | Assigned project |
| `supervisor` | FK User | Assigned supervisor |
| `assigned_by` | FK User | Coordinator who assigned |
| `assigned_at` | DateTime | Assignment timestamp |
| `notes` | TextField | Assignment notes |

## 8.4 DraftSubmission

| Field | Type | Description |
|---|---|---|
| `project` | FK ResearchProject | Related project |
| `chapter` | PositiveSmallInteger | Chapter 1 to Chapter 5 |
| `version` | PositiveInteger | Draft version |
| `file` | FileField | Uploaded draft file |
| `file_hash` | CharField | SHA-256 hash |
| `status` | CharField | submitted, approved, rejected, revision_required |
| `submitted_by` | FK User | Uploading student |
| `submitted_at` | DateTime | Submission timestamp |

Constraint:

- Unique combination of project, chapter, and version.

## 8.5 Feedback

| Field | Type | Description |
|---|---|---|
| `draft` | FK DraftSubmission | Reviewed draft |
| `supervisor` | FK User | Reviewer |
| `decision` | CharField | approved, rejected, revision_required |
| `comments` | TextField | Supervisor comments |
| `progress_score` | PositiveSmallInteger | 0 to 100 |
| `created_at` | DateTime | Feedback timestamp |

## 8.6 Notification

| Field | Type | Description |
|---|---|---|
| `recipient` | FK User | Notification recipient |
| `title` | CharField | Notification title |
| `message` | TextField | Notification content |
| `notification_type` | CharField | info, approval, feedback, deadline, warning |
| `url` | CharField | Optional target URL |
| `is_read` | Boolean | Read state |
| `created_at` | DateTime | Creation timestamp |

## 8.7 ActivityLog

| Field | Type | Description |
|---|---|---|
| `actor` | FK User nullable | Authenticated actor |
| `action` | CharField | Request action label |
| `object_type` | CharField | Optional object type |
| `object_id` | CharField | Optional object ID |
| `path` | CharField | Request path |
| `method` | CharField | HTTP method |
| `ip_address` | GenericIPAddressField | Source IP |
| `user_agent` | TextField | Browser/client metadata |
| `created_at` | DateTime | Log timestamp |

---

# 9. Security Requirements and Controls

## 9.1 Authentication Security

- Django authentication shall manage session-based authentication.
- Passwords shall be stored using Django's password hashing system.
- Role-specific login validation shall prevent users from entering through the wrong role interface.

## 9.2 Authorization Security

Role access is enforced using mixins:

- `StudentRequiredMixin`
- `SupervisorRequiredMixin`
- `CoordinatorRequiredMixin`

Coordinator access allows users whose role is coordinator or who are Django staff users.

## 9.3 Input Validation

The system validates:

- Role-specific registration fields.
- CSV extension and maximum file size.
- Required CSV columns.
- Allowed bulk upload roles.
- Draft file extension and maximum file size.
- Feedback progress score maximum.

## 9.4 CSRF Protection

Django CSRF middleware is enabled and applies to form submissions.

## 9.5 File Upload Security

Draft uploads are restricted to:

- `.pdf`
- `.doc`
- `.docx`

Draft file size must not exceed 5MB.

CSV upload file size must not exceed 2MB.

## 9.6 Audit Security

Authenticated mutating requests are logged with actor, method, path, IP address, user agent, and timestamp.

## 9.7 Configuration Security

Sensitive configuration is loaded using environment variables through `python-decouple`:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

Production deployments must set `DEBUG=False` and use a secure secret key.

## 9.8 Security Risks and Recommended Mitigations

| Risk | Current Control | Recommendation |
|---|---|---|
| Accidental commit of `.env` | `.env.example` exists | Ensure `.env` is ignored by Git |
| CSV data injection | Basic validation | Sanitize exported CSV data if export feature is added |
| Unauthorized object access | Role querysets in list views | Add object-level checks to detail views where needed |
| File content malware | Extension and size validation | Add antivirus scanning in production |
| Brute-force login | Django auth | Add rate limiting or account lockout |
| Session hijacking | Django sessions | Enforce HTTPS and secure cookie settings in production |

---

# 10. Business Rules

## 10.1 User Rules

- A user has one primary role.
- Students require `student_id`.
- Supervisors and coordinators require `staff_id` during registration.
- Bulk upload creates only students and supervisors.
- Student eligibility for assignment is represented by `is_verified=True`.

## 10.2 Project Rules

- Projects are created by students.
- Coordinators assign supervisors.
- Each project has at most one `SupervisorAssignment` record.
- Assignment changes project status to `Under Review`.
- Approval changes project status to `Approved`.

## 10.3 Draft Rules

- Drafts are associated with projects.
- Draft versions are unique per project and chapter.
- New draft versions are calculated from latest existing version.
- Draft feedback updates draft status.

## 10.4 Feedback Rules

- Only assigned supervisors can provide feedback for a draft.
- Progress score cannot exceed 100.
- Feedback decision maps directly to draft status.

---

# 11. User Interface Requirements

## 11.1 General UI

- The UI shall use responsive templates and Bootstrap-compatible styling.
- Pages shall use consistent cards, forms, tables, and navigation.
- Sidebar navigation shall show role-relevant links.

## 11.2 Login UI

- Login page shall present role selection for Student, Supervisor, and Coordinator.
- Selected role shall be passed to the authentication form.

## 11.3 Coordinator Manage Users UI

The Manage Users page shall include:

- Bulk Upload tab.
- Single User tab.
- Bulk Assignments tab.
- Student and supervisor overview tables.
- Eligible student count.
- Upload rules and CSV guidance.

## 11.4 Student UI

Students shall have styled pages for:

- Topic submission.
- Draft upload.
- Draft listing.
- Dashboard progress.

## 11.5 Coordinator Assignment UI

Supervisor assignment page shall display:

- Project summary.
- Assignment form.
- Assignment checklist and workflow guidance.

---

# 12. External Interfaces

## 12.1 Database Interface

The default database is SQLite configured through Django ORM.

## 12.2 File Storage Interface

Uploaded draft files are stored under media storage using the path pattern:

```text
drafts/project_<project_id>/chapter_<chapter>/v<version>.<extension>
```

## 12.3 Browser Interface

Users interact with the system through server-rendered HTML templates.

## 12.4 Environment Configuration Interface

Configuration values are read from environment variables or `.env` files using `python-decouple`.

---

# 13. Testing Methodology

## 13.1 Testing Objectives

Testing shall verify:

- Role validation.
- User creation workflows.
- Bulk upload processing.
- Bulk assignment processing.
- Project assignment side effects.
- File upload validation.
- Feedback status transitions.
- Dashboard access and filtering.
- Authorization boundaries.

## 13.2 Existing Automated Tests

The current test suite includes account-level tests covering:

- User role helper properties.
- Coordinator bulk upload for students and supervisors.
- Eligible student upload.
- Single user creation.
- Bulk assignment of eligible students to supervisors.

## 13.3 Recommended Unit Tests

### Accounts

- Registration requires student ID for students.
- Registration requires staff ID for supervisors and coordinators.
- Incorrect role login is rejected.
- Coordinator-only user management blocks non-coordinators.
- Bulk upload skips invalid roles.
- Bulk upload updates existing users.

### Projects

- Student can create project.
- Supervisor cannot create project.
- Coordinator can approve project.
- Coordinator can assign supervisor manually.
- Assignment updates project status.
- Assignment triggers notification.

### Drafts

- Student can upload valid draft.
- Invalid extension is rejected.
- Oversized file is rejected.
- Version increments correctly.
- File hash is generated.

### Feedbacks

- Assigned supervisor can submit feedback.
- Unassigned supervisor cannot submit feedback.
- Progress score above 100 is rejected.
- Feedback decision updates draft status.

### Notifications

- Notification is created for assignment.
- Notification is created for feedback.
- Notification read status can be updated.

### Audit

- POST requests create activity logs.
- GET requests do not create activity logs.

## 13.4 Integration Testing

Recommended integration scenarios:

1. Coordinator uploads eligible students and supervisors, then performs bulk assignment.
2. Student submits topic, coordinator assigns supervisor, student uploads draft, supervisor gives feedback.
3. Coordinator manually creates supervisor, assigns project, verifies dashboard workload changes.
4. Invalid CSV upload returns validation errors and does not corrupt existing data.

## 13.5 Security Testing

Security testing shall include:

- Authentication bypass attempts.
- Role escalation attempts.
- CSRF submission checks.
- CSV upload validation checks.
- File upload extension bypass attempts.
- Unauthorized feedback creation attempts.
- Direct URL access tests for role-protected views.

## 13.6 User Acceptance Testing

UAT shall verify:

- Coordinators can onboard a cohort of eligible students.
- Coordinators can upload supervisors by department.
- Coordinators can assign students to supervisors in bulk.
- Students can submit topics and drafts without confusion.
- Supervisors can review pending drafts efficiently.
- Dashboards reflect real workflow state.

## 13.7 Test Execution Commands

Recommended commands:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py test accounts
```

---

# 14. Deployment and Configuration Requirements

## 14.1 Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 14.2 Environment Variables

Required or recommended variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django cryptographic signing key |
| `DEBUG` | Debug mode flag |
| `ALLOWED_HOSTS` | Allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins |

## 14.3 Production Requirements

For production deployment:

- Set `DEBUG=False`.
- Use a strong `SECRET_KEY`.
- Configure production database such as PostgreSQL.
- Configure static file hosting.
- Configure media file storage.
- Enforce HTTPS.
- Set secure session and CSRF cookie settings.
- Add logging and monitoring.
- Ensure `.env` is not committed to version control.

---

# 15. Traceability Matrix

| Requirement | Implementation Area | Verification |
|---|---|---|
| FR-001 Role login | `accounts.forms.RoleAuthenticationForm`, `accounts.views.UserLoginView` | Login tests, manual role checks |
| FR-004 Bulk upload | `accounts.views.UserManagementView.form_valid` | Account tests |
| FR-005 Single user | `SingleUserCreateForm`, `UserManagementView.post` | Account tests |
| FR-006 Bulk assignment | `BulkAssignmentUploadForm`, `process_bulk_assignments` | Account tests |
| FR-007 Topic submission | `projects.views.ProjectCreateView` | Project tests |
| FR-011 Manual assignment | `SupervisorAssignmentView` | Project tests |
| FR-012 Draft upload | `DraftUploadView`, `DraftSubmission`, validators | Draft tests |
| FR-014 Feedback | `FeedbackCreateView`, `FeedbackForm` | Feedback tests |
| FR-015 Notifications | `notifications.services.notify_user` | Integration tests |
| FR-021 Audit logging | `audit.middleware.ActivityLogMiddleware` | Audit tests |

---

# 16. Assumptions, Constraints, and Future Enhancements

## 16.1 Assumptions

- Each user has one primary role.
- Students upload chapter drafts after project creation.
- Coordinators are trusted administrative users.
- `is_verified` is used as the eligibility flag for student assignment.
- Supervisors are matched manually or through CSV mapping rather than automated department matching.

## 16.2 Constraints

- Current database configuration uses SQLite.
- Current interface is server-rendered rather than API-first.
- Bulk uploads are limited to CSV files up to 2MB.
- Draft uploads are limited to PDF, DOC, and DOCX files up to 5MB.

## 16.3 Recommended Future Enhancements

- Add explicit `eligible_for_project` field separate from `is_verified` for clearer domain modelling.
- Add automated supervisor matching by department and workload.
- Add coordinator review queue for invalid CSV rows.
- Add downloadable CSV templates.
- Add import preview before committing bulk changes.
- Add supervisor workload capacity limits.
- Add email notifications.
- Add REST API endpoints for mobile or external integration.
- Add advanced audit trail with object IDs and model names.
- Add comprehensive object-level permission tests.
- Add production-ready PostgreSQL configuration.

---

# Appendix A: CSV Templates

## A.1 Bulk User Upload Template

```csv
username,email,role,first_name,last_name,department,student_id,staff_id,phone,password,eligible
student1,student1@example.com,student,John,Doe,Computer Science,S001,,0800000000,StrongPass123,true
supervisor1,supervisor1@example.com,supervisor,Jane,Smith,Computer Science,,F001,0900000000,StrongPass123,
```

## A.2 Bulk Assignment Template

```csv
student_username,supervisor_username,project_title,notes
student1,supervisor1,AI Research Project,Department match
```

---

# Appendix B: Quality Attributes

| Attribute | Requirement |
|---|---|
| Security | RBAC, CSRF, validated uploads, hashed passwords |
| Maintainability | Modular Django apps and reusable forms/mixins |
| Reliability | Constraints, validated workflows, audit logs |
| Usability | Role dashboards and guided coordinator tabs |
| Scalability | Query optimizations and bulk upload constraints |
| Auditability | ActivityLog middleware and timestamped domain records |

---

# Appendix C: Current Verification Status

At the time of analysis, targeted checks previously executed successfully:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test accounts
```

The account test suite includes coverage for the coordinator bulk management workflow.
