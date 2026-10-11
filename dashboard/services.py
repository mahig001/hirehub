"""Services for dashboard app."""
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from accounts.models import User
from jobs.models import Job
from applications.models import Application
from companies.models import Company


class AdminDashboardService:
    """Service for admin dashboard statistics and charts."""
    
    @classmethod
    def get_stats(cls):
        """Get overall statistics for admin dashboard."""
        return {
            'total_users': User.objects.count(),
            'active_jobs': Job.objects.filter(is_active=True, is_approved=True).count(),
            'total_applications': Application.objects.count(),
            'pending_companies': Company.objects.filter(status=Company.PENDING).count(),
        }
    
    @classmethod
    def get_users_chart_data(cls):
        """Get user registration data for last 30 days."""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        users_by_date = User.objects.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Convert to list of dicts with date string
        return [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            }
            for item in users_by_date
        ]
    
    @classmethod
    def get_jobs_chart_data(cls):
        """Get job posting data for last 30 days."""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        jobs_by_date = Job.objects.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            }
            for item in jobs_by_date
        ]
    
    @classmethod
    def get_applications_chart_data(cls):
        """Get application data for last 30 days."""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        apps_by_date = Application.objects.filter(
            applied_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('applied_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            }
            for item in apps_by_date
        ]
