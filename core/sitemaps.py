"""
Sitemaps for HireHub.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from jobs.models import Job
from companies.models import Company


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return [
            'core:home',
            'core:about',
            'core:contact',
            'core:faq',
            'core:privacy_policy',
            'core:terms_of_service',
        ]
    
    def location(self, item):
        return reverse(item)


class JobSitemap(Sitemap):
    """Sitemap for job listings."""
    
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Job.objects.filter(is_active=True, is_approved=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CompanySitemap(Sitemap):
    """Sitemap for company profiles."""
    
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return Company.objects.filter(status=Company.VERIFIED)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()
