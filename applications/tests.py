"""Tests for applications app."""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from jobs.models import Job, Category
from companies.models import Company
from .models import Application, ApplicationStatusHistory
from .services import ApplicationService

User = get_user_model()


class ApplicationServiceTests(TestCase):
    """Test ApplicationService methods."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.job_seeker = User.objects.create_user(
            email='seeker@test.com',
            password='testpass123',
            first_name='John',
            last_name='Seeker',
            role='USER'
        )
        
        self.recruiter = User.objects.create_user(
            email='recruiter@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Recruiter',
            role='EMPLOYEE'
        )
        
        # Create company
        self.company = Company.objects.create(
            owner=self.recruiter,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='A test company'
        )
        
        # Create category
        self.category = Category.objects.create(name='Software Engineering')
        
        # Create job
        self.job = Job.objects.create(
            company=self.company,
            title='Senior Engineer',
            description='A senior engineering role',
            category=self.category,
            location='San Francisco',
            job_type='FULL_TIME',
            is_active=True,
            is_approved=True
        )
    
    def test_create_application_success(self):
        """Test successful application creation."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker,
            cover_letter='I am interested in this role.'
        )
        
        self.assertEqual(app.job, self.job)
        self.assertEqual(app.applicant, self.job_seeker)
        self.assertEqual(app.status, Application.PENDING)
        self.assertEqual(app.cover_letter, 'I am interested in this role.')
        
        # Check history was created
        self.assertEqual(app.status_history.count(), 1)
        history = app.status_history.first()
        self.assertEqual(history.new_status, Application.PENDING)
        self.assertEqual(history.changed_by, self.job_seeker)
    
    def test_create_application_duplicate_prevention(self):
        """Test that duplicate applications are prevented."""
        # Create first application
        ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker,
            cover_letter='First application'
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError) as context:
            ApplicationService.create_application(
                job=self.job,
                applicant=self.job_seeker,
                cover_letter='Second application'
            )
        
        self.assertIn('already applied', str(context.exception))
    
    def test_change_status_success(self):
        """Test successful status change."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
        
        # Change status to REVIEWING
        updated_app = ApplicationService.change_status(
            app,
            Application.REVIEWING,
            self.recruiter,
            'Application under review'
        )
        
        self.assertEqual(updated_app.status, Application.REVIEWING)
        
        # Check history
        self.assertEqual(updated_app.status_history.count(), 2)
        latest_change = updated_app.status_history.first()
        self.assertEqual(latest_change.old_status, Application.PENDING)
        self.assertEqual(latest_change.new_status, Application.REVIEWING)
        self.assertEqual(latest_change.changed_by, self.recruiter)
        self.assertEqual(latest_change.note, 'Application under review')
    
    def test_change_status_invalid_status(self):
        """Test that invalid status is rejected."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
        
        with self.assertRaises(ValidationError):
            ApplicationService.change_status(
                app,
                'INVALID_STATUS',
                self.recruiter
            )
    
    def test_withdraw_application_success(self):
        """Test successful application withdrawal."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
        
        # Withdraw application
        withdrawn_app = ApplicationService.withdraw_application(app, self.job_seeker)
        
        self.assertEqual(withdrawn_app.status, Application.WITHDRAWN)
        self.assertEqual(withdrawn_app.status_history.count(), 2)
    
    def test_withdraw_application_not_applicant(self):
        """Test that non-applicants cannot withdraw."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
        
        with self.assertRaises(ValidationError) as context:
            ApplicationService.withdraw_application(app, self.recruiter)
        
        self.assertIn('own applications', str(context.exception))
    
    def test_withdraw_application_already_withdrawn(self):
        """Test that already withdrawn applications cannot be withdrawn again."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
        
        # Withdraw once
        ApplicationService.withdraw_application(app, self.job_seeker)
        
        # Try to withdraw again
        app.refresh_from_db()
        with self.assertRaises(ValidationError) as context:
            ApplicationService.withdraw_application(app, self.job_seeker)
        
        self.assertIn('already been withdrawn', str(context.exception))
    
    def test_get_status_history(self):
        """Test retrieving status history."""
        app = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
        
        # Make status changes
        ApplicationService.change_status(
            app,
            Application.REVIEWING,
            self.recruiter,
            'First review'
        )
        
        ApplicationService.change_status(
            app,
            Application.SHORTLISTED,
            self.recruiter,
            'Candidate shortlisted'
        )
        
        # Get history
        history = ApplicationService.get_status_history(app)
        self.assertEqual(history.count(), 3)
        
        # Check order (most recent first)
        statuses = [h.new_status for h in history]
        self.assertEqual(statuses[0], Application.SHORTLISTED)
        self.assertEqual(statuses[1], Application.REVIEWING)
        self.assertEqual(statuses[2], Application.PENDING)


class ApplicationViewTests(TestCase):
    """Test application views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create users
        self.job_seeker = User.objects.create_user(
            email='seeker@test.com',
            password='testpass123',
            first_name='John',
            last_name='Seeker',
            role='USER'
        )
        
        self.recruiter = User.objects.create_user(
            email='recruiter@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Recruiter',
            role='EMPLOYEE'
        )
        
        self.other_recruiter = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        
        # Create companies
        self.company = Company.objects.create(
            owner=self.recruiter,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='A test company'
        )
        
        self.other_company = Company.objects.create(
            owner=self.other_recruiter,
            name='Other Company',
            industry='finance',
            size='51-200',
            location='New York',
            about='Another company'
        )
        
        # Create category
        self.category = Category.objects.create(name='Software Engineering')
        
        # Create jobs
        self.job = Job.objects.create(
            company=self.company,
            title='Senior Engineer',
            description='A senior engineering role',
            category=self.category,
            location='San Francisco',
            job_type='FULL_TIME',
            is_active=True,
            is_approved=True
        )
        
        self.other_job = Job.objects.create(
            company=self.other_company,
            title='Data Analyst',
            description='A data analyst role',
            category=self.category,
            location='New York',
            job_type='FULL_TIME',
            is_active=True,
            is_approved=True
        )
    
    def test_apply_view_unauthorized(self):
        """Test that non-job-seekers cannot apply."""
        self.client.force_login(self.recruiter)
        
        response = self.client.get(reverse('applications:apply', kwargs={'job_pk': self.job.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_apply_view_not_authenticated(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse('applications:apply', kwargs={'job_pk': self.job.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_apply_view_authenticated_job_seeker(self):
        """Test that job seekers can access apply view."""
        self.client.force_login(self.job_seeker)
        
        response = self.client.get(reverse('applications:apply', kwargs={'job_pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['job'], self.job)
    
    def test_apply_form_submission_success(self):
        """Test successful application submission."""
        self.client.force_login(self.job_seeker)
        
        response = self.client.post(
            reverse('applications:apply', kwargs={'job_pk': self.job.pk}),
            {'cover_letter': 'I am very interested in this position.'}
        )
        
        # Should create application
        app = Application.objects.get(job=self.job, applicant=self.job_seeker)
        self.assertEqual(app.status, Application.PENDING)
        self.assertEqual(app.cover_letter, 'I am very interested in this position.')
        
        # Should redirect to detail view
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(app.pk), response.url)
    
    def test_apply_form_duplicate_prevention(self):
        """Test that duplicate applications are prevented."""
        # Create first application
        ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker,
            cover_letter='First application'
        )
        
        # Try to apply again
        self.client.force_login(self.job_seeker)
        response = self.client.post(
            reverse('applications:apply', kwargs={'job_pk': self.job.pk}),
            {'cover_letter': 'Second application'}
        )
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
        # Check that URL contains the job slug (for job detail redirect)
        self.assertIn(self.job.slug, response.url)
    
    def test_my_applications_list_access(self):
        """Test that only job seekers can access their applications list."""
        self.client.force_login(self.recruiter)
        
        response = self.client.get(reverse('applications:my_applications'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_my_applications_list_job_seeker(self):
        """Test job seeker can view their applications."""
        # Create applications
        ApplicationService.create_application(self.job, self.job_seeker)
        ApplicationService.create_application(self.other_job, self.job_seeker)
        
        self.client.force_login(self.job_seeker)
        response = self.client.get(reverse('applications:my_applications'))
        
        self.assertEqual(response.status_code, 200)
        applications = response.context['applications']
        self.assertEqual(applications.count(), 2)
    
    def test_withdraw_application_success(self):
        """Test successful application withdrawal."""
        app = ApplicationService.create_application(self.job, self.job_seeker)
        
        self.client.force_login(self.job_seeker)
        response = self.client.post(reverse('applications:withdraw', kwargs={'pk': app.pk}))
        
        app.refresh_from_db()
        self.assertEqual(app.status, Application.WITHDRAWN)
    
    def test_withdraw_application_not_own(self):
        """Test that users cannot withdraw others' applications."""
        app = ApplicationService.create_application(self.job, self.job_seeker)
        
        self.client.force_login(self.recruiter)
        response = self.client.post(reverse('applications:withdraw', kwargs={'pk': app.pk}))
        
        # Should get 404 or 403
        self.assertIn(response.status_code, [302, 403, 404])
    
    def test_job_applicants_list_access(self):
        """Test that job seekers cannot access applicants list."""
        self.client.force_login(self.job_seeker)
        
        response = self.client.get(
            reverse('applications:job_applicants', kwargs={'pk': self.job.pk})
        )
        # Should get 403 or redirect
        self.assertIn(response.status_code, [302, 403])
    
    def test_job_applicants_list_recruiter_own_company(self):
        """Test that recruiters can view applicants for their company's jobs."""
        # Create applications
        ApplicationService.create_application(self.job, self.job_seeker)
        
        self.client.force_login(self.recruiter)
        response = self.client.get(
            reverse('applications:job_applicants', kwargs={'pk': self.job.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        applications = response.context['applications']
        self.assertEqual(applications.count(), 1)
    
    def test_job_applicants_list_recruiter_other_company(self):
        """Test that recruiters cannot view applicants for other companies' jobs."""
        ApplicationService.create_application(self.job, self.job_seeker)
        
        self.client.force_login(self.other_recruiter)
        response = self.client.get(
            reverse('applications:job_applicants', kwargs={'pk': self.job.pk})
        )
        
        # Should get 403 or redirect
        self.assertIn(response.status_code, [302, 403])
    
    def test_application_detail_view_job_seeker_own(self):
        """Test that job seekers can view their own applications."""
        app = ApplicationService.create_application(self.job, self.job_seeker)
        
        self.client.force_login(self.job_seeker)
        response = self.client.get(reverse('applications:detail', kwargs={'pk': app.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['application'], app)
    
    def test_application_detail_view_job_seeker_other(self):
        """Test that job seekers cannot view other's applications."""
        other_seeker = User.objects.create_user(
            email='other_seeker@test.com',
            password='testpass123',
            role='USER'
        )
        app = ApplicationService.create_application(self.job, other_seeker)
        
        self.client.force_login(self.job_seeker)
        response = self.client.get(reverse('applications:detail', kwargs={'pk': app.pk}))
        
        self.assertEqual(response.status_code, 404)


class InterviewModelTests(TestCase):
    """Test Interview model."""
    
    def setUp(self):
        """Set up test data."""
        self.job_seeker = User.objects.create_user(
            email='seeker@test.com',
            password='testpass123',
            role='USER'
        )
        
        self.recruiter = User.objects.create_user(
            email='recruiter@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        
        self.company = Company.objects.create(
            owner=self.recruiter,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='A test company'
        )
        
        self.category = Category.objects.create(name='Software Engineering')
        
        self.job = Job.objects.create(
            company=self.company,
            title='Senior Engineer',
            description='A senior engineering role',
            category=self.category,
            location='San Francisco',
            job_type='FULL_TIME',
            is_active=True,
            is_approved=True
        )
        
        self.application = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
    
    def test_interview_creation(self):
        """Test creating an interview."""
        from applications.models import Interview
        from datetime import datetime, timedelta
        
        scheduled_time = datetime.now() + timedelta(days=1)
        
        interview = Interview.objects.create(
            application=self.application,
            scheduled_at=scheduled_time,
            interview_type='VIDEO',
            location='https://zoom.us/j/123456',
            notes='Technical round',
            interviewer=self.recruiter
        )
        
        self.assertEqual(interview.application, self.application)
        self.assertEqual(interview.interview_type, 'VIDEO')
        self.assertEqual(interview.location, 'https://zoom.us/j/123456')
        self.assertEqual(interview.interviewer, self.recruiter)


class ExtendedApplicationServiceTests(TestCase):
    """Test extended ApplicationService methods."""
    
    def setUp(self):
        """Set up test data."""
        self.job_seeker = User.objects.create_user(
            email='seeker@test.com',
            password='testpass123',
            role='USER'
        )
        
        self.recruiter = User.objects.create_user(
            email='recruiter@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        
        self.company = Company.objects.create(
            owner=self.recruiter,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='A test company'
        )
        
        self.category = Category.objects.create(name='Software Engineering')
        
        self.job = Job.objects.create(
            company=self.company,
            title='Senior Engineer',
            description='A senior engineering role',
            category=self.category,
            location='San Francisco',
            job_type='FULL_TIME',
            is_active=True,
            is_approved=True
        )
        
        self.application = ApplicationService.create_application(
            job=self.job,
            applicant=self.job_seeker
        )
    
    def test_bulk_change_status(self):
        """Test bulk status change."""
        app2 = ApplicationService.create_application(
            self.job,
            User.objects.create_user(
                email='seeker2@test.com',
                password='testpass123',
                role='USER'
            )
        )
        
        app3 = ApplicationService.create_application(
            self.job,
            User.objects.create_user(
                email='seeker3@test.com',
                password='testpass123',
                role='USER'
            )
        )
        
        application_ids = [self.application.id, app2.id, app3.id]
        
        updated = ApplicationService.bulk_change_status(
            application_ids,
            Application.REVIEWING,
            self.recruiter,
            'Bulk review started'
        )
        
        self.assertEqual(len(updated), 3)
        
        # Refresh and check
        self.application.refresh_from_db()
        app2.refresh_from_db()
        app3.refresh_from_db()
        
        self.assertEqual(self.application.status, Application.REVIEWING)
        self.assertEqual(app2.status, Application.REVIEWING)
        self.assertEqual(app3.status, Application.REVIEWING)
    
    def test_add_applicant_note(self):
        """Test adding a note to application."""
        note_text = 'Great candidate with strong Python skills'
        
        ApplicationService.add_applicant_note(self.application, note_text)
        
        self.application.refresh_from_db()
        self.assertIn(note_text, self.application.recruiter_notes)
        self.assertIn('[', self.application.recruiter_notes)  # Timestamp marker
    
    def test_rate_applicant(self):
        """Test rating an applicant."""
        ApplicationService.rate_applicant(self.application, 4)
        
        self.application.refresh_from_db()
        self.assertEqual(self.application.rating, 4)
    
    def test_rate_applicant_invalid(self):
        """Test that invalid ratings are rejected."""
        with self.assertRaises(ValidationError):
            ApplicationService.rate_applicant(self.application, 6)
        
        with self.assertRaises(ValidationError):
            ApplicationService.rate_applicant(self.application, 0)


class EmployeeViewTests(TestCase):
    """Test employee-specific views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.job_seeker = User.objects.create_user(
            email='seeker@test.com',
            password='testpass123',
            role='USER'
        )
        
        self.recruiter = User.objects.create_user(
            email='recruiter@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        
        self.other_recruiter = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        
        self.company = Company.objects.create(
            owner=self.recruiter,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='San Francisco',
            about='A test company'
        )
        
        self.other_company = Company.objects.create(
            owner=self.other_recruiter,
            name='Other Company',
            industry='finance',
            size='51-200',
            location='New York',
            about='Another company'
        )
        
        self.category = Category.objects.create(name='Software Engineering')
        
        self.job = Job.objects.create(
            company=self.company,
            title='Senior Engineer',
            description='A senior engineering role',
            category=self.category,
            location='San Francisco',
            job_type='FULL_TIME',
            is_active=True,
            is_approved=True
        )
        
        self.application = ApplicationService.create_application(
            self.job,
            self.job_seeker
        )
    
    def test_bulk_action_view_permission(self):
        """Test that non-employees cannot access bulk action view."""
        self.client.force_login(self.job_seeker)
        
        response = self.client.post(
            reverse('applications:bulk_action', kwargs={'job_pk': self.job.pk}),
            {
                'application_ids': [self.application.pk],
                'action': 'REVIEWING'
            }
        )
        
        # Should get 302 (redirect) or 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_export_csv_view(self):
        """Test CSV export returns correct content type."""
        self.client.force_login(self.recruiter)
        
        response = self.client.get(
            reverse('applications:export_csv', kwargs={'job_pk': self.job.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_applicant_detail_view_company_check(self):
        """Test that recruiters can only view applicants for their company's jobs."""
        self.client.force_login(self.other_recruiter)
        
        response = self.client.get(
            reverse('applications:applicant_detail', kwargs={'pk': self.application.pk})
        )
        
        # Should get 404 since application is not for their company
        self.assertEqual(response.status_code, 404)
