from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from companies.models import Company
from jobs.models import Job, JobReport, Category


class ReportJobViewTests(TestCase):
    """Tests for ReportJobView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.USER
        )
        self.company_owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            first_name='Owner',
            last_name='User',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.company_owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='Test City',
            about='Test about',
            status=Company.VERIFIED
        )
        self.category = Category.objects.create(name='Technology')
        self.job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test description',
            location='Test Location',
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
        self.url = reverse('jobs:report', kwargs={'pk': self.job.pk})
    
    def test_requires_login(self):
        """Test that reporting a job requires login."""
        response = self.client.get(self.url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_creates_job_report(self):
        """Test that submitting the form creates a job report."""
        self.client.force_login(self.user)
        
        # Verify no reports exist
        self.assertEqual(JobReport.objects.count(), 0)
        
        # Submit report
        response = self.client.post(self.url, {
            'reason': 'SPAM',
            'description': 'This job is spam'
        })
        
        # Verify report was created
        self.assertEqual(JobReport.objects.count(), 1)
        report = JobReport.objects.first()
        self.assertEqual(report.job, self.job)
        self.assertEqual(report.reporter, self.user)
        self.assertEqual(report.reason, 'SPAM')
        self.assertEqual(report.description, 'This job is spam')
        self.assertEqual(report.status, JobReport.PENDING)
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
