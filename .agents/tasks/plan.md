# Implementation Plan: HireHub Phases 2-10

This plan has been decomposed into FEAT artifacts for structured execution. See `.agents/tasks/hirehub-phases-2-10/` for detailed feature definitions.

## Overview

Complete the HireHub job-finding platform with 9 major features covering Companies & Jobs, Job Seeker Profiles, Applications, Employee Dashboard, Admin Console, Notifications, Hardening, DevOps, and Final Verification.

**Base context:** Django 5.1.3 at c:\Users\arjun\mahi\mahi with Phase 1 complete (custom User model, split settings, full authentication). Python venv at C:\Users\arjun\mahi\venv\Scripts\python.exe.

## Feature Breakdown

### FEAT-001: Phase 2 - Companies & Jobs
- Company CRUD with admin approval workflow
- Category, Skill, and Employee models
- Job model with full-text search using SearchVector
- Public job listing with django-filter (category/skill/location/job_type)
- JOB_MODERATION_ENABLED setting integration

### FEAT-002: Phase 3 - Job Seeker Profiles
- JobSeekerProfile with completeness calculation (0-100%)
- Education and Experience models with CRUD
- Resume upload to private storage with permission-checked serving
- Saved jobs M2M with toggle functionality
- Profile completeness meter with Bootstrap progress bar

### FEAT-003: Phase 4 - Applications
- Application model with status (PENDING, REVIEWING, SHORTLISTED, REJECTED, WITHDRAWN)
- ApplicationStatusHistory audit trail
- ApplicationService for status transitions and notifications
- Apply flow with duplicate prevention
- Job seeker dashboard with status timeline

### FEAT-004: Phase 5 - Employee Dashboard
- Interview model for scheduling
- Applicant management with filters/sorting
- Notes and ratings on applicants
- Bulk actions (bulk reject, bulk shortlist)
- CSV export of applicants
- Employee dashboard with stats

### FEAT-005: Phase 6 - Admin Console
- Admin dashboard at /manage/ with Chart.js statistics
- User/Company/Job management
- Job moderation queue (if JOB_MODERATION_ENABLED)
- JobReport and ContactMessage models
- AuditLog for tracking admin actions

### FEAT-006: Phase 7 - Notifications
- Notification model with signals for application events
- Email templates for status changes, interviews, alerts
- JobAlert model for job seeker subscriptions
- Management commands: send_job_alerts, expire_jobs
- Notification bell with unread count in navbar

### FEAT-007: Phase 8 - Hardening
- Custom 403/404/500 error pages
- sitemap.xml with django.contrib.sitemaps
- robots.txt view
- SEO meta tags (og:, twitter:, canonical)
- Comprehensive tests for all apps
- >= 80% test coverage with coverage.py

### FEAT-008: Phase 9 - DevOps
- Multi-stage Dockerfile with non-root user
- docker-compose.yml (nginx/gunicorn/postgres)
- GitHub Actions CI workflow (ruff + tests)
- Management command seed_demo for realistic data
- README.md and docs/SYSTEM_DESIGN.md with Mermaid diagrams

### FEAT-009: Phase 10 - Final Verification
- Full test suite execution
- check and check --deploy validation
- Migration consistency verification
- Manual test checklist execution (3 role flows)
- docs/TESTING.md documentation

## Verification Pattern

Each feature follows:
1. Run makemigrations and migrate for new models
2. Run check --deploy
3. Run tests for affected apps
4. Manual smoke test of new functionality
5. Commit with descriptive message

## Final Deliverable

Fully functional HireHub platform with:
- 3 role-based flows (Job Seeker, Recruiter, Admin)
- Job posting, application, and tracking system
- Email notifications and alerts
- Admin moderation and reporting
- Docker deployment ready
- >= 80% test coverage
- Comprehensive documentation
