from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile, Education, Experience
from jobs.models import Job, Category
from companies.models import Company
from datetime import date
import io

User = get_user_model()


class JobSeekerProfileModelTest(TestCase):
    """Tests for JobSeekerProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='jobseeker@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=User.USER
        )
        self.profile = JobSeekerProfile.objects.create(user=self.user)
    
    def test_profile_creation(self):
        """Test that profile is created successfully."""
        self.assertEqual(str(self.profile), "John Doe's Profile")
        self.assertEqual(self.profile.user, self.user)
    
    def test_calculate_completeness_empty(self):
        """Test completeness calculation with empty profile."""
        completeness = self.profile.calculate_completeness()
        self.assertEqual(completeness, 0)
    
    def test_calculate_completeness_partial(self):
        """Test completeness calculation with partial data."""
        self.profile.headline = "Software Engineer"
        self.profile.bio = "Test bio"
        self.profile.location = "New York"
        self.profile.phone = "1234567890"
        self.profile.save()
        
        completeness = self.profile.calculate_completeness()
        # 4 fields out of 8 = 50%
        self.assertEqual(completeness, 50)
    
    def test_calculate_completeness_with_education(self):
        """Test completeness calculation with education."""
        self.profile.headline = "Software Engineer"
        self.profile.bio = "Test bio"
        self.profile.save()
        
        Education.objects.create(
            user=self.user,
            degree="Bachelor's",
            field_of_study="Computer Science",
            institution="Test University",
            start_date=date(2015, 9, 1),
            end_date=date(2019, 6, 1)
        )
        
        completeness = self.profile.calculate_completeness()
        # 2 profile fields + 1 education = 3 out of 8 = 37%
        self.assertEqual(completeness, 37)
    
    def test_calculate_completeness_with_experience(self):
        """Test completeness calculation with experience."""
        self.profile.headline = "Software Engineer"
        self.profile.save()
        
        Experience.objects.create(
            user=self.user,
            title="Developer",
            company_name="Test Company",
            start_date=date(2020, 1, 1),
            is_current=True
        )
        
        completeness = self.profile.calculate_completeness()
        # 1 profile field + 1 experience = 2 out of 8 = 25%
        self.assertEqual(completeness, 25)
    
    def test_calculate_completeness_full(self):
        """Test completeness calculation with all fields filled."""
        # Create a simple file for avatar and resume
        avatar_file = SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")
        resume_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        
        self.profile.headline = "Software Engineer"
        self.profile.bio = "Test bio"
        self.profile.location = "New York"
        self.profile.phone = "1234567890"
        self.profile.avatar = avatar_file
        self.profile.resume = resume_file
        self.profile.save()
        
        Education.objects.create(
            user=self.user,
            degree="Bachelor's",
            field_of_study="Computer Science",
            institution="Test University",
            start_date=date(2015, 9, 1)
        )
        
        Experience.objects.create(
            user=self.user,
            title="Developer",
            company_name="Test Company",
            start_date=date(2020, 1, 1),
            is_current=True
        )
        
        completeness = self.profile.calculate_completeness()
        # All 8 fields filled = 100%
        self.assertEqual(completeness, 100)


class EducationModelTest(TestCase):
    """Tests for Education model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            role=User.USER
        )
    
    def test_education_creation(self):
        """Test education creation and ordering."""
        edu1 = Education.objects.create(
            user=self.user,
            degree="Bachelor's",
            field_of_study="Computer Science",
            institution="University A",
            start_date=date(2015, 9, 1)
        )
        edu2 = Education.objects.create(
            user=self.user,
            degree="Master's",
            field_of_study="Data Science",
            institution="University B",
            start_date=date(2019, 9, 1)
        )
        
        # Check that more recent education comes first
        educations = list(Education.objects.all())
        self.assertEqual(educations[0], edu2)
        self.assertEqual(educations[1], edu1)
        
        # Check string representation
        expected_str = "Bachelor's in Computer Science at University A"
        self.assertEqual(str(edu1), expected_str)


class ExperienceModelTest(TestCase):
    """Tests for Experience model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            role=User.USER
        )
    
    def test_experience_creation(self):
        """Test experience creation."""
        exp = Experience.objects.create(
            user=self.user,
            title="Software Developer",
            company_name="Tech Corp",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31)
        )
        
        self.assertEqual(str(exp), "Software Developer at Tech Corp")
        self.assertFalse(exp.is_current)
    
    def test_experience_is_current_clears_end_date(self):
        """Test that is_current clears end_date."""
        exp = Experience.objects.create(
            user=self.user,
            title="Developer",
            company_name="Company X",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            is_current=True
        )
        
        # end_date should be None when is_current is True
        self.assertIsNone(exp.end_date)
        self.assertTrue(exp.is_current)


class ResumeDownloadViewTest(TestCase):
    """Tests for resume download permission checks."""
    
    def setUp(self):
        self.client = Client()
        
        # Create job seeker
        self.job_seeker = User.objects.create_user(
            email='seeker@test.com',
            password='testpass123',
            role=User.USER
        )
        self.profile = JobSeekerProfile.objects.create(user=self.job_seeker)
        
        # Create resume file
        resume_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        self.profile.resume = resume_file
        self.profile.save()
        
        # Create recruiter
        self.recruiter = User.objects.create_user(
            email='recruiter@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        
        # Create another user (not owner)
        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            role=User.USER
        )
    
    def test_owner_can_download_resume(self):
        """Test that owner can download their own resume."""
        self.client.force_login(self.job_seeker)
        response = self.client.get(
            reverse('accounts:resume_download', kwargs={'user_id': self.job_seeker.id})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_recruiter_can_download_resume(self):
        """Test that recruiter can download resume."""
        self.client.force_login(self.recruiter)
        response = self.client.get(
            reverse('accounts:resume_download', kwargs={'user_id': self.job_seeker.id})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_other_user_cannot_download_resume(self):
        """Test that other users cannot download resume."""
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse('accounts:resume_download', kwargs={'user_id': self.job_seeker.id})
        )
        self.assertEqual(response.status_code, 403)
    
    def test_anonymous_user_cannot_download_resume(self):
        """Test that anonymous users are redirected to login."""
        response = self.client.get(
            reverse('accounts:resume_download', kwargs={'user_id': self.job_seeker.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class ProfileViewsTest(TestCase):
    """Tests for profile views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            role=User.USER
        )
        self.client.force_login(self.user)
    
    def test_profile_detail_view_creates_profile(self):
        """Test that viewing profile creates it if it doesn't exist."""
        response = self.client.get(reverse('accounts:profile_detail'))
        self.assertEqual(response.status_code, 200)
        
        # Check that profile was created
        self.assertTrue(JobSeekerProfile.objects.filter(user=self.user).exists())
    
    def test_profile_edit_view(self):
        """Test profile edit view."""
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)
        
        # Test updating profile
        response = self.client.post(reverse('accounts:profile_edit'), {
            'headline': 'Test Headline',
            'bio': 'Test Bio',
            'location': 'New York',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify profile was updated
        profile = JobSeekerProfile.objects.get(user=self.user)
        self.assertEqual(profile.headline, 'Test Headline')
        self.assertEqual(profile.bio, 'Test Bio')


class SavedJobsTest(TestCase):
    """Tests for saved jobs functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            role=User.USER
        )
        self.profile = JobSeekerProfile.objects.create(user=self.user)
        
        # Create a company owner
        self.company_owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            role=User.EMPLOYEE
        )
        
        # Create a company and job
        self.company = Company.objects.create(
            owner=self.company_owner,
            name='Test Company',
            slug='test-company',
            industry='technology',
            size='11-50',
            location='New York',
            about='Test about'
        )
        self.category = Category.objects.create(name='Engineering', slug='engineering')
        self.job = Job.objects.create(
            company=self.company,
            title='Software Engineer',
            description='Test job description',
            location='New York',
            category=self.category,
            is_active=True,
            is_approved=True
        )
        
        self.client.force_login(self.user)
    
    def test_toggle_saved_job_add(self):
        """Test adding a job to saved jobs."""
        response = self.client.post(
            reverse('accounts:toggle_saved_job', kwargs={'pk': self.job.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['saved'])
        
        # Verify job is saved
        self.assertIn(self.job, self.profile.saved_jobs.all())
    
    def test_toggle_saved_job_remove(self):
        """Test removing a job from saved jobs."""
        # First add the job
        self.profile.saved_jobs.add(self.job)
        
        # Then remove it
        response = self.client.post(
            reverse('accounts:toggle_saved_job', kwargs={'pk': self.job.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['saved'])
        
        # Verify job is not saved
        self.assertNotIn(self.job, self.profile.saved_jobs.all())
    
    def test_saved_jobs_list_view(self):
        """Test saved jobs list view."""
        # Add a job to saved
        self.profile.saved_jobs.add(self.job)
        
        response = self.client.get(reverse('accounts:saved_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)
