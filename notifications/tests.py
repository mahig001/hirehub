from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, Category
from companies.models import Company
from applications.models import Application, Interview
from .models import Notification, JobAlert
from .services import NotificationService
from io import StringIO
from django.core.management import call_command

User = get_user_model()


class NotificationModelTest(TestCase):
    """Tests for Notification model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='USER'
        )
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.APPLICATION_STATUS_CHANGED,
            title='Test Notification',
            message='This is a test message',
            link='/test-link/'
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.notification_type, Notification.APPLICATION_STATUS_CHANGED)
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
    
    def test_notification_str(self):
        """Test notification string representation."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.JOB_ALERT,
            title='Job Alert',
            message='Test message'
        )
        
        expected = f'{self.user} - Job Alert'
        self.assertEqual(str(notification), expected)


class NotificationServiceTest(TestCase):
    """Tests for NotificationService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='USER'
        )
    
    def test_create_notification(self):
        """Test creating notification via service."""
        notification = NotificationService.create_notification(
            recipient=self.user,
            notification_type=Notification.JOB_ALERT,
            title='Service Test',
            message='Test message',
            link='/test/'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, 'Service Test')
    
    def test_get_unread_count(self):
        """Test getting unread notification count."""
        # Create some notifications
        NotificationService.create_notification(
            self.user,
            Notification.JOB_ALERT,
            'Test 1',
            'Message 1'
        )
        NotificationService.create_notification(
            self.user,
            Notification.JOB_ALERT,
            'Test 2',
            'Message 2'
        )
        
        count = NotificationService.get_unread_count(self.user)
        self.assertEqual(count, 2)
    
    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = NotificationService.create_notification(
            self.user,
            Notification.JOB_ALERT,
            'Test',
            'Message'
        )
        
        success = NotificationService.mark_as_read(notification.id, self.user)
        self.assertTrue(success)
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read."""
        # Create multiple notifications
        for i in range(3):
            NotificationService.create_notification(
                self.user,
                Notification.JOB_ALERT,
                f'Test {i}',
                f'Message {i}'
            )
        
        count = NotificationService.mark_all_as_read(self.user)
        self.assertEqual(count, 3)
        
        unread_count = NotificationService.get_unread_count(self.user)
        self.assertEqual(unread_count, 0)


class SignalTest(TestCase):
    """Tests for notification signals."""
    
    def setUp(self):
        # Create users
        self.recruiter = User.objects.create_user(
            email='recruiter@example.com',
            password='testpass123',
            first_name='Recruiter',
            last_name='User',
            role='EMPLOYEE'
        )
        
        self.applicant = User.objects.create_user(
            email='applicant@example.com',
            password='testpass123',
            first_name='Job',
            last_name='Seeker',
            role='USER'
        )
        
        # Create company
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company',
            owner=self.recruiter,
            industry='technology',
            size='11-50',
            location='Test Location',
            about='Test description'
        )
        from companies.models import Employee
        Employee.objects.create(
            user=self.recruiter,
            company=self.company,
            position='Recruiter',
            is_primary=True
        )
        
        # Create category
        self.category = Category.objects.create(name='IT')
        
        # Create job
        self.job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test description',
            category=self.category,
            location='Test Location',
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
    
    def test_on_application_created_signal(self):
        """Test that creating an application triggers notification."""
        # Create application
        application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            cover_letter='Test cover letter'
        )
        
        # Check notification was created for recruiter
        notifications = Notification.objects.filter(
            recipient=self.recruiter,
            notification_type=Notification.NEW_APPLICANT
        )
        self.assertTrue(notifications.exists())
    
    def test_on_application_status_changed_signal(self):
        """Test that changing application status triggers notification."""
        # Create application
        application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            cover_letter='Test cover letter'
        )
        
        # Clear any existing notifications
        Notification.objects.all().delete()
        
        # Change status
        application.status = Application.SHORTLISTED
        application.save()
        
        # Check notification was created for applicant
        notifications = Notification.objects.filter(
            recipient=self.applicant,
            notification_type=Notification.APPLICATION_STATUS_CHANGED
        )
        self.assertTrue(notifications.exists())
    
    def test_on_interview_scheduled_signal(self):
        """Test that scheduling an interview triggers notification."""
        # Create application
        application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            cover_letter='Test cover letter'
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        
        # Schedule interview
        interview = Interview.objects.create(
            application=application,
            scheduled_at=timezone.now() + timedelta(days=7),
            interview_type=Interview.PHONE,
            location='Remote'
        )
        
        # Check notification was created
        notifications = Notification.objects.filter(
            recipient=self.applicant,
            notification_type=Notification.INTERVIEW_SCHEDULED
        )
        self.assertTrue(notifications.exists())


class SendJobAlertsCommandTest(TestCase):
    """Tests for send_job_alerts management command."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='USER'
        )
        
        # Create recruiter for company owner
        self.recruiter = User.objects.create_user(
            email='recruiter@example.com',
            password='testpass123',
            first_name='Recruiter',
            last_name='User',
            role='EMPLOYEE'
        )
        
        # Create company
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company',
            owner=self.recruiter,
            industry='technology',
            size='11-50',
            location='Test Location',
            about='Test description'
        )
        
        # Create category
        self.category = Category.objects.create(name='IT')
    
    def test_send_job_alerts_command(self):
        """Test that send_job_alerts command processes alerts."""
        # Create job alert
        alert = JobAlert.objects.create(
            user=self.user,
            category=self.category,
            frequency=JobAlert.DAILY,
            is_active=True
        )
        
        # Create matching job
        job = Job.objects.create(
            company=self.company,
            title='Test Job',
            description='Test description',
            category=self.category,
            location='Test Location',
            job_type=Job.FULL_TIME,
            is_active=True,
            is_approved=True
        )
        
        # Run command
        out = StringIO()
        call_command('send_job_alerts', stdout=out)
        
        # Check alert was updated
        alert.refresh_from_db()
        self.assertIsNotNone(alert.last_sent_at)


class ExpireJobsCommandTest(TestCase):
    """Tests for expire_jobs management command."""
    
    def setUp(self):
        self.recruiter = User.objects.create_user(
            email='recruiter@example.com',
            password='testpass123',
            first_name='Recruiter',
            last_name='User',
            role='EMPLOYEE'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company',
            owner=self.recruiter,
            industry='technology',
            size='11-50',
            location='Test Location',
            about='Test description'
        )
        from companies.models import Employee
        Employee.objects.create(
            user=self.recruiter,
            company=self.company,
            position='Recruiter',
            is_primary=True
        )
        
        self.category = Category.objects.create(name='IT')
    
    def test_expire_jobs_command(self):
        """Test that expire_jobs command marks jobs inactive."""
        # Create job with past deadline
        past_date = timezone.now().date() - timedelta(days=5)
        job = Job.objects.create(
            company=self.company,
            title='Expired Job',
            description='Test description',
            category=self.category,
            location='Test Location',
            job_type=Job.FULL_TIME,
            deadline=past_date,
            is_active=True,
            is_approved=True
        )
        
        # Run command
        out = StringIO()
        call_command('expire_jobs', stdout=out)
        
        # Check job is now inactive
        job.refresh_from_db()
        self.assertFalse(job.is_active)


class NotificationViewTest(TestCase):
    """Tests for notification views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='USER'
        )
    
    def test_notification_list_requires_login(self):
        """Test that notification list requires authentication."""
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_notification_list_authenticated(self):
        """Test notification list view for authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notification_list.html')
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read."""
        # Create notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                notification_type=Notification.JOB_ALERT,
                title=f'Test {i}',
                message=f'Message {i}'
            )
        
        self.client.force_login(self.user)
        response = self.client.post(reverse('notifications:mark_all_read'))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check all are marked as read
        unread = Notification.objects.filter(recipient=self.user, is_read=False).count()
        self.assertEqual(unread, 0)
