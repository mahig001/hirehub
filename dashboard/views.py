"""Views for employee dashboard."""
from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Q
from accounts.mixins import EmployeeRoleMixin
from applications.models import Application, Interview
from companies.models import Company


class EmployeeDashboardView(EmployeeRoleMixin, TemplateView):
    """Dashboard view for recruiters/employees."""
    
    template_name = 'dashboard/employee_dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add dashboard stats and recent activity to context."""
        context = super().get_context_data(**kwargs)
        
        try:
            company = self.request.user.company
            
            # Get all applications for company's jobs
            company_applications = Application.objects.filter(job__company=company)
            
            # Stats
            context['total_applicants'] = company_applications.count()
            context['pending_count'] = company_applications.filter(status=Application.PENDING).count()
            context['shortlisted_count'] = company_applications.filter(status=Application.SHORTLISTED).count()
            
            # Upcoming interviews in next 7 days
            today = datetime.now()
            next_week = today + timedelta(days=7)
            context['upcoming_interviews'] = Interview.objects.filter(
                application__job__company=company,
                scheduled_at__gte=today,
                scheduled_at__lte=next_week
            ).count()
            
            # Recent activity - latest 5 applications
            context['recent_applications'] = company_applications.select_related(
                'job', 'applicant'
            ).order_by('-applied_at')[:5]
            
        except Company.DoesNotExist:
            # If user is not associated with a company
            context['total_applicants'] = 0
            context['pending_count'] = 0
            context['shortlisted_count'] = 0
            context['upcoming_interviews'] = 0
            context['recent_applications'] = []
        
        return context
