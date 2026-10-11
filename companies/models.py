from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse


class Company(models.Model):
    """Company model for employers."""
    
    PENDING = 'PENDING'
    VERIFIED = 'VERIFIED'
    REJECTED = 'REJECTED'
    SUSPENDED = 'SUSPENDED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending Verification'),
        (VERIFIED, 'Verified'),
        (REJECTED, 'Rejected'),
        (SUSPENDED, 'Suspended'),
    ]
    
    INDUSTRY_CHOICES = [
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('media', 'Media & Entertainment'),
        ('real_estate', 'Real Estate'),
        ('other', 'Other'),
    ]
    
    SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees'),
    ]
    
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    location = models.CharField(max_length=200)
    about = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'companies'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['industry']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            counter = 1
            original_slug = self.slug
            while Company.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('companies:detail', kwargs={'slug': self.slug})
    
    def can_post_jobs(self):
        """Check if company can post jobs."""
        return self.status in [self.PENDING, self.VERIFIED]
    
    @property
    def is_verified(self):
        return self.status == self.VERIFIED


class Employee(models.Model):
    """Employee model for company staff."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employments'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    position = models.CharField(max_length=100)
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary contact for the company'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
        unique_together = [['user', 'company']]
        indexes = [
            models.Index(fields=['user', 'company']),
        ]
    
    def __str__(self):
        return f'{self.user.get_full_name()} at {self.company.name}'
