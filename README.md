# Research Project Supervision Management System

Enterprise-grade Django system for managing research topics, supervisors, draft submissions, feedback, analytics, notifications, and audit logs.

## Setup

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

## Apps

- `accounts`: users, roles, authentication, access mixins.
- `projects`: research topics, approvals, supervisor assignment.
- `drafts`: chapter uploads, versioning, file validation.
- `feedbacks`: reviews, decisions, progress scores.
- `dashboard`: role dashboards and analytics.
- `notifications`: user alerts and reminders.
- `audit`: activity logging and request metadata.
