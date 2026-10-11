from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('role', User.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email as username and role-based access."""
    
    USER = 'USER'
    EMPLOYEE = 'EMPLOYEE'
    ADMIN = 'ADMIN'
    
    ROLE_CHOICES = [
        (USER, 'Job Seeker'),
        (EMPLOYEE, 'Recruiter'),
        (ADMIN, 'Admin'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip() or self.email
    
    def get_dashboard_url(self):
        """Return the dashboard URL based on user role."""
        if self.role == self.USER:
            return '/user/dashboard/'
        elif self.role == self.EMPLOYEE:
            return '/employee/dashboard/'
        elif self.role == self.ADMIN:
            return '/manage/'
        return '/'


class JobSeekerProfile(models.Model):
    """Extended profile for job seekers."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='job_seeker_profile',
        limit_choices_to={'role': User.USER}
    )
    headline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    resume = models.FileField(
        upload_to='private/resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    saved_jobs = models.ManyToManyField('jobs.Job', blank=True, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
    
    def calculate_completeness(self):
        """Calculate profile completeness percentage (0-100)."""
        fields = [
            self.headline,
            self.bio,
            self.location,
            self.phone,
            self.avatar,
            self.resume,
        ]
        
        # Count filled profile fields (6 total)
        filled = sum(1 for field in fields if field)
        
        # Count education entries
        education_count = self.user.education_set.count()
        has_education = 1 if education_count > 0 else 0
        
        # Count experience entries
        experience_count = self.user.experience_set.count()
        has_experience = 1 if experience_count > 0 else 0
        
        # Total: 6 profile fields + education + experience = 8 total
        total_fields = 8
        filled_fields = filled + has_education + has_experience
        
        return int((filled_fields / total_fields) * 100)


class Education(models.Model):
    """Education history for users."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='education_set'
    )
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date']),
        ]
        verbose_name_plural = "Education"
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} at {self.institution}"


class Experience(models.Model):
    """Work experience history for users."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='experience_set'
    )
    title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    def save(self, *args, **kwargs):
        """Clear end_date if is_current is True."""
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)
