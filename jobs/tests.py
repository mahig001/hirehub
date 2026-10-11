from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from companies.models import Company
from jobs.models import Job, JobReport, Category, Skill


class JobModelTests(TestCase):
    """Tests for Job model."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='Test City',
            about='Test about',
            status=Company.VERIFIED
        )
        self.category = Category.objects.create(name='Technology')
    
    def test_job_str_representation(self):
        """Test job string representation."""
        job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='Test description',
            location='San Francisco',
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
        expected_str = f'Software Engineer at {self.company.name}'
        self.assertEqual(str(job), expected_str)
    
    def test_job_get_absolute_url(self):
        """Test job get_absolute_url method."""
        job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test description',
            location='Test Location',
            job_type=Job.FULL_TIME
        )
        expected_url = reverse('jobs:detail', kwargs={'slug': job.slug})
        self.assertEqual(job.get_absolute_url(), expected_url)
    
    def test_job_salary_range_property(self):
        """Test salary_range property formats correctly."""
        job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test',
            location='Test',
            job_type=Job.FULL_TIME,
            salary_min=50000,
            salary_max=80000
        )
        self.assertEqual(job.salary_range, '$50,000 - $80,000')
        
        job_min_only = Job.objects.create(
            company=self.company,
            title='Test Job 2',
            description='Test',
            location='Test',
            job_type=Job.FULL_TIME,
            salary_min=50000
        )
        self.assertEqual(job_min_only.salary_range, 'From $50,000')


class CategoryModelTests(TestCase):
    """Tests for Category model."""
    
    def test_category_str_representation(self):
        """Test category string representation."""
        category = Category.objects.create(name='Engineering')
        self.assertEqual(str(category), 'Engineering')
    
    def test_category_slug_generation(self):
        """Test that slug is generated from name."""
        category = Category.objects.create(name='Software Development')
        self.assertEqual(category.slug, 'software-development')


class JobReportModelTests(TestCase):
    """Tests for JobReport model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            role=User.USER
        )
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='Test City',
            about='Test about',
            status=Company.VERIFIED
        )
        self.job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test description',
            location='Test Location',
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
    
    def test_job_report_creation_with_default_status(self):
        """Test that JobReport is created with default PENDING status."""
        report = JobReport.objects.create(
            job=self.job,
            reporter=self.user,
            reason=JobReport.SPAM,
            description='This is spam'
        )
        self.assertEqual(report.status, JobReport.PENDING)
        self.assertEqual(report.reason, JobReport.SPAM)


class JobListViewTests(TestCase):
    """Tests for job list view."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='Test City',
            about='Test',
            status=Company.VERIFIED
        )
        self.category = Category.objects.create(name='Engineering')
        self.job1 = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='Test',
            location='San Francisco',
            category=self.category,
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
        self.job2 = Job.objects.create(
            company=self.company,
            title='Data Analyst',
            description='Test',
            location='New York',
            category=self.category,
            job_type=Job.PART_TIME,
            is_active=True,
            is_approved=True
        )
        self.url = reverse('jobs:list')
    
    def test_job_list_view_filter_by_category(self):
        """Test filtering jobs by category."""
        response = self.client.get(self.url, {'category': self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer')
        self.assertContains(response, 'Data Analyst')
    
    def test_job_list_view_filter_by_job_type(self):
        """Test filtering jobs by job_type."""
        response = self.client.get(self.url, {'job_type': Job.FULL_TIME})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer')


class JobDetailViewTests(TestCase):
    """Tests for job detail view."""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        self.company = Company.objects.create(
            owner=self.owner,
            name='Test Company',
            industry='technology',
            size='11-50',
            location='Test City',
            about='Test',
            status=Company.VERIFIED
        )
        self.job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test description',
            location='Test Location',
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
    
    def test_job_detail_view_shows_job(self):
        """Test that job detail view displays job information."""
        url = reverse('jobs:detail', kwargs={'slug': self.job.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)
        self.assertContains(response, self.job.description)
    
    def test_job_detail_view_404_for_nonexistent_job(self):
        """Test 404 for non-existent job."""
        url = reverse('jobs:detail', kwargs={'slug': 'nonexistent-job'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


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
