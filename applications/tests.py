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
