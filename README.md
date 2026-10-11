# HireHub - Job Finding Platform

A professional, production-quality Django job-finding platform with role-based access control for job seekers, recruiters, and administrators.

## Features

### For Job Seekers (USER Role)
- ✅ User registration with email verification
- ✅ Complete profile management with resume upload
- ✅ Education and work experience tracking
- ✅ Profile completeness meter
- ✅ Job search with advanced filters
- ✅ Save jobs for later viewing
- ✅ Apply to jobs with cover letter and custom resume
- ✅ Application tracking with status timeline
- ✅ Withdraw applications
- ✅ Job alerts (daily/weekly email notifications)
- ✅ In-app notifications for status changes
- ✅ Dashboard with application statistics

### For Recruiters (EMPLOYEE Role)
- ✅ Company profile management
- ✅ Job posting with rich details (CRUD operations)
- ✅ Draft, publish, close, and reopen jobs
- ✅ Applicant management per job
- ✅ Filter applicants by status, keyword, date
- ✅ Rate applicants (1-5 stars)
- ✅ Add private notes to applications
- ✅ Schedule interviews with applicants
- ✅ Bulk status updates for multiple applicants
- ✅ CSV export of applicant data
- ✅ Dashboard with hiring statistics
- ✅ Notifications for new applications

### For Administrators (ADMIN Role)
- ✅ Admin console at /manage/ with platform statistics
- ✅ User management (activate/deactivate, change roles)
- ✅ Company verification/rejection/suspension
- ✅ Job moderation queue (approve/reject with reason)
- ✅ Review job abuse reports
- ✅ Contact message management
- ✅ Audit log of admin actions
- ✅ Full Django admin access as fallback

### Public Features
- ✅ Job listing with search and filters
- ✅ Job detail pages with company information
- ✅ Company directory and profiles
- ✅ Responsive Bootstrap 5.3 design
- ✅ SEO-friendly with meta tags
- ✅ Custom error pages (403, 404, 500)

## Tech Stack

- **Backend**: Django 5.1.3, Python 3.12+
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript, Chart.js
- **Forms**: django-crispy-forms with crispy-bootstrap5
- **Authentication**: Custom User model with email login, django-axes for throttling
- **Search/Filter**: django-filter, PostgreSQL full-text search
- **File Storage**: Pillow for images, private storage for resumes
- **Static Files**: WhiteNoise
- **Server**: Gunicorn
- **Dev Tools**: ruff for linting, coverage for test coverage

## Installation

### Prerequisites
- Python 3.12 or higher
- pip and virtualenv
- PostgreSQL (for production) or SQLite (for development)

### Quick Start (Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hirehub
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load demo data (optional)**
   ```bash
   python manage.py seed_demo
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Homepage: http://localhost:8000/
   - Django Admin: http://localhost:8000/django-admin/
   - Admin Console: http://localhost:8000/manage/

### Demo Accounts (After running seed_demo)

- **Admin**: admin@hirehub.local / admin123
- **Recruiter 1**: recruiter1@company1.com / recruiter123
- **Recruiter 2**: recruiter2@company2.com / recruiter123
- **Job Seeker 1**: seeker1@example.com / seeker123
- **Job Seeker 2**: seeker2@example.com / seeker123
- **Job Seeker 3**: seeker3@example.com / seeker123

## Project Structure

```
hirehub/
├── accounts/          # User authentication and profiles
├── applications/      # Job application management
├── companies/         # Company profiles and management
├── core/             # Home, static pages, utilities
├── dashboard/        # Admin console
├── jobs/             # Job listings and search
├── notifications/    # In-app and email notifications
├── config/           # Django settings
│   └── settings/
│       ├── base.py   # Shared settings
│       ├── dev.py    # Development settings
│       └── prod.py   # Production settings
├── static/           # Static files (CSS, JS, images)
├── templates/        # HTML templates
├── media/            # User-uploaded public files
├── private/          # Private file storage (resumes)
├── requirements/     # Python dependencies
│   ├── base.txt      # Core dependencies
│   ├── dev.txt       # Development dependencies
│   └── prod.txt      # Production dependencies
└── manage.py
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.dev

# Database
DATABASE_URL=sqlite:///db.sqlite3
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/hirehub

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# or for production:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# Application
JOB_MODERATION_ENABLED=True
```

## Management Commands

### seed_demo
Create demo data for development and testing:
```bash
python manage.py seed_demo
```

Creates:
- 1 admin user
- 2 recruiters with companies
- 5 job seekers with complete profiles
- 10 job categories
- 30 skills
- 25 jobs across different categories
- Sample applications in various statuses

### send_job_alerts
Send email alerts to users with active job alerts:
```bash
python manage.py send_job_alerts
```

### expire_jobs
Mark jobs past their deadline as expired:
```bash
python manage.py expire_jobs
```

## Testing

### Run all tests
```bash
python manage.py test
```

### Run tests with coverage
```bash
coverage run manage.py test
coverage report
coverage html  # Generate HTML report
```

### Run specific app tests
```bash
python manage.py test accounts
python manage.py test applications
```

### Linting
```bash
ruff check .
ruff format .
```

## Deployment

### Using Docker

1. **Build and run with docker-compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Application: http://localhost/
   - Static files served by nginx

### Manual Deployment

1. **Set production environment variables**
2. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start with Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Configure nginx** to serve static files and proxy to Gunicorn

## Security Features

- ✅ Email-based authentication (no usernames)
- ✅ Email verification required
- ✅ Password strength validation
- ✅ Login throttling (django-axes)
- ✅ CSRF protection
- ✅ Secure password reset flow
- ✅ Role-based access control (RBAC)
- ✅ Object-level permissions (no IDOR)
- ✅ Private file storage for resumes
- ✅ Secure headers in production
- ✅ Input validation and sanitization

## Key URLs

### Public
- `/` - Homepage
- `/jobs/` - Job listing
- `/jobs/<slug>/` - Job detail
- `/companies/` - Company directory
- `/companies/<slug>/` - Company profile
- `/about/` - About page
- `/contact/` - Contact form
- `/faq/` - FAQ

### Authentication
- `/accounts/register/` - Registration
- `/accounts/login/` - Login
- `/accounts/logout/` - Logout
- `/accounts/password-reset/` - Password reset
- `/accounts/verify/<token>/` - Email verification

### Job Seeker (USER)
- `/user/dashboard/` - Dashboard
- `/user/profile/` - Profile management
- `/user/applications/` - My applications
- `/user/saved/` - Saved jobs
- `/user/alerts/` - Job alerts

### Recruiter (EMPLOYEE)
- `/employee/dashboard/` - Dashboard
- `/employee/company/` - Company profile
- `/employee/jobs/` - My jobs
- `/employee/jobs/create/` - Post new job
- `/employee/jobs/<id>/applicants/` - Applicant management
- `/employee/applications/<id>/` - Application detail

### Admin
- `/manage/` - Admin console
- `/manage/users/` - User management
- `/manage/companies/` - Company verification
- `/manage/jobs/` - Job moderation
- `/manage/reports/` - Abuse reports
- `/django-admin/` - Django admin (fallback)

## Assumptions

- Job seekers register with role=USER, recruiters with role=EMPLOYEE
- Admin users are created via `createsuperuser` or by existing admins
- Companies require verification before posting jobs (can be disabled via `JOB_MODERATION_ENABLED=False`)
- Job moderation is enabled by default
- Resumes are stored privately and only accessible to: the owner, recruiters viewing their applications, and admins
- Applications cannot be withdrawn once an offer is made
- Job alerts are sent based on frequency setting (daily or weekly)
- Jobs past their deadline are automatically marked as expired

## Known Limitations

- Single resume per job seeker (can upload different resume per application)
- No real-time notifications (uses polling)
- Email alerts sent via management command (requires cron job or task scheduler)
- Basic search functionality (keyword + location, no advanced filters like salary range in search)
- No API endpoints (all functionality is web-based)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Run linting: `ruff check . && ruff format .`
6. Submit a pull request

## License

This project is for educational/demonstration purposes.

## Support

For issues or questions, please open an issue on GitHub.

---

**Built with Django 5.1.3 | Bootstrap 5.3 | PostgreSQL**
