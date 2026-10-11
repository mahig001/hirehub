from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.postgres.search import SearchVectorField
from django.conf import settings
from companies.models import Company


class Category(models.Model):
    """Job category model."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Skill(models.Model):
    """Skill model for job requirements."""
    
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """Job posting model."""
    
    FULL_TIME = 'FULL_TIME'
    PART_TIME = 'PART_TIME'
    CONTRACT = 'CONTRACT'
    INTERNSHIP = 'INTERNSHIP'
    
    JOB_TYPE_CHOICES = [
        (FULL_TIME, 'Full-time'),
        (PART_TIME, 'Part-time'),
        (CONTRACT, 'Contract'),
        (INTERNSHIP, 'Internship'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')
    skills = models.ManyToManyField(Skill, related_name='jobs', blank=True)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default=FULL_TIME)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True, help_text='Application deadline')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, help_text='Admin approval for moderation')
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['location']),
            models.Index(fields=['job_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['posted_at']),
        ]
    
    def __str__(self):
        return f'{self.title} at {self.company.name}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.company.name} {self.title}')
            # Ensure unique slug
            counter = 1
            original_slug = self.slug
            while Job.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        
        # Auto-approve if moderation is disabled
        if not settings.JOB_MODERATION_ENABLED and not self.pk:
            self.is_approved = True
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'slug': self.slug})
    
    @property
    def salary_range(self):
        """Return formatted salary range."""
        if self.salary_min and self.salary_max:
            return f'${self.salary_min:,.0f} - ${self.salary_max:,.0f}'
        elif self.salary_min:
            return f'From ${self.salary_min:,.0f}'
        elif self.salary_max:
            return f'Up to ${self.salary_max:,.0f}'
        return 'Not specified'


class JobReport(models.Model):
    """Job report model for flagging inappropriate jobs."""
    
    SPAM = 'SPAM'
    INAPPROPRIATE = 'INAPPROPRIATE'
    FRAUD = 'FRAUD'
    OTHER = 'OTHER'
    
    REASON_CHOICES = [
        (SPAM, 'Spam'),
        (INAPPROPRIATE, 'Inappropriate'),
        (FRAUD, 'Fraud'),
        (OTHER, 'Other'),
    ]
    
    PENDING = 'PENDING'
    REVIEWED = 'REVIEWED'
    RESOLVED = 'RESOLVED'
    DISMISSED = 'DISMISSED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (REVIEWED, 'Reviewed'),
        (RESOLVED, 'Resolved'),
        (DISMISSED, 'Dismissed'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'Report for {self.job.title} by {self.reporter.get_full_name()}'
