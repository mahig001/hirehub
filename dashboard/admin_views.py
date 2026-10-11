"""Admin views for dashboard app."""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView, View
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from accounts.models import User
from accounts.mixins import AdminRoleMixin
from companies.models import Company
from jobs.models import Job, JobReport
from core.models import ContactMessage, AuditLog
from core.services import AuditLogService
from .services import AdminDashboardService


class AdminDashboardView(AdminRoleMixin, TemplateView):
    """Main admin dashboard with statistics and charts."""
    
    template_name = 'dashboard/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = AdminDashboardService.get_stats()
        context['users_chart_data'] = json.dumps(AdminDashboardService.get_users_chart_data())
        context['jobs_chart_data'] = json.dumps(AdminDashboardService.get_jobs_chart_data())
        context['applications_chart_data'] = json.dumps(AdminDashboardService.get_applications_chart_data())
        return context


class UserListView(AdminRoleMixin, ListView):
    """List all users with search and filter."""
    
    model = User
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        # Search by username or email
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filter by role
        role = self.request.GET.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by is_active
        is_active = self.request.GET.get('is_active', '')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['is_active_filter'] = self.request.GET.get('is_active', '')
        context['role_choices'] = User.ROLE_CHOICES
        return context


class UserDetailView(AdminRoleMixin, DetailView):
    """View user details."""
    
    model = User
    template_name = 'dashboard/user_detail.html'
    context_object_name = 'user_obj'


class UserToggleActiveView(AdminRoleMixin, View):
    """Toggle user active status."""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        
        action = 'USER_ACTIVATED' if user.is_active else 'USER_DEACTIVATED'
        AuditLogService.log_action(
            actor=request.user,
            action=action,
            target_model='User',
            target_id=user.pk,
            details={'email': user.email, 'new_status': user.is_active},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.email} has been {status}.')
        return redirect('dashboard:user_detail', pk=user.pk)


class CompanyManagementListView(AdminRoleMixin, ListView):
    """List all companies with filter."""
    
    model = Company
    template_name = 'dashboard/company_management.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Company.objects.select_related('owner').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Company.STATUS_CHOICES
        return context


class CompanyApprovalView(AdminRoleMixin, View):
    """Approve a company."""
    
    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.status = Company.VERIFIED
        company.save()
        
        AuditLogService.log_action(
            actor=request.user,
            action='COMPANY_APPROVED',
            target_model='Company',
            target_id=company.pk,
            details={'name': company.name},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Company "{company.name}" has been approved.')
        return redirect('dashboard:company_management')


class CompanyRejectionView(AdminRoleMixin, View):
    """Reject a company."""
    
    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        reason = request.POST.get('reason', '')
        
        company.status = Company.REJECTED
        company.rejection_reason = reason
        company.save()
        
        AuditLogService.log_action(
            actor=request.user,
            action='COMPANY_REJECTED',
            target_model='Company',
            target_id=company.pk,
            details={'name': company.name, 'reason': reason},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Company "{company.name}" has been rejected.')
        return redirect('dashboard:company_management')


class JobManagementListView(AdminRoleMixin, ListView):
    """List all jobs with filter."""
    
    model = Job
    template_name = 'dashboard/job_management.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Job.objects.select_related('company', 'category').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'approved':
            queryset = queryset.filter(is_approved=True)
        elif status == 'pending':
            queryset = queryset.filter(is_approved=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class JobModerationQueueView(AdminRoleMixin, ListView):
    """List jobs awaiting moderation."""
    
    model = Job
    template_name = 'dashboard/job_moderation_queue.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        return Job.objects.filter(
            is_approved=False
        ).select_related('company', 'category').order_by('-created_at')


class JobApprovalView(AdminRoleMixin, View):
    """Approve a job."""
    
    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        job.is_approved = True
        job.is_active = True
        job.save()
        
        AuditLogService.log_action(
            actor=request.user,
            action='JOB_APPROVED',
            target_model='Job',
            target_id=job.pk,
            details={'title': job.title, 'company': job.company.name},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Job "{job.title}" has been approved.')
        return redirect('dashboard:job_moderation_queue')


class JobRejectionView(AdminRoleMixin, View):
    """Reject a job."""
    
    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        reason = request.POST.get('reason', '')
        
        job.is_active = False
        job.save()
        
        AuditLogService.log_action(
            actor=request.user,
            action='JOB_REJECTED',
            target_model='Job',
            target_id=job.pk,
            details={'title': job.title, 'company': job.company.name, 'reason': reason},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'Job "{job.title}" has been rejected.')
        return redirect('dashboard:job_moderation_queue')


class JobReportsListView(AdminRoleMixin, ListView):
    """List all job reports."""
    
    model = JobReport
    template_name = 'dashboard/job_report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = JobReport.objects.select_related(
            'job', 'job__company', 'reporter'
        ).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class JobReportDetailView(AdminRoleMixin, DetailView):
    """View and handle job report."""
    
    model = JobReport
    template_name = 'dashboard/job_report_detail.html'
    context_object_name = 'report'
    
    def post(self, request, pk):
        report = self.get_object()
        action_type = request.POST.get('action')
        
        if action_type == 'resolve':
            report.status = JobReport.RESOLVED
            report.reviewed_at = timezone.now()
            report.reviewed_by = request.user
            report.save()
            
            AuditLogService.log_action(
                actor=request.user,
                action='REPORT_RESOLVED',
                target_model='JobReport',
                target_id=report.pk,
                details={'job_title': report.job.title, 'reason': report.reason},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Report has been resolved.')
        
        elif action_type == 'dismiss':
            report.status = JobReport.DISMISSED
            report.reviewed_at = timezone.now()
            report.reviewed_by = request.user
            report.save()
            
            AuditLogService.log_action(
                actor=request.user,
                action='REPORT_DISMISSED',
                target_model='JobReport',
                target_id=report.pk,
                details={'job_title': report.job.title, 'reason': report.reason},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Report has been dismissed.')
        
        return redirect('dashboard:job_report_detail', pk=report.pk)


class ContactMessagesListView(AdminRoleMixin, ListView):
    """List all contact messages."""
    
    model = ContactMessage
    template_name = 'dashboard/contact_messages.html'
    context_object_name = 'messages_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ContactMessage.objects.order_by('-created_at')
        
        # Filter by is_read
        is_read = self.request.GET.get('is_read', '')
        if is_read == 'true':
            queryset = queryset.filter(is_read=True)
        elif is_read == 'false':
            queryset = queryset.filter(is_read=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_read_filter'] = self.request.GET.get('is_read', '')
        return context


class ContactMessageDetailView(AdminRoleMixin, DetailView):
    """View contact message."""
    
    model = ContactMessage
    template_name = 'dashboard/contact_message_detail.html'
    context_object_name = 'message'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Mark as read when viewed
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save()
        return response
    
    def post(self, request, pk):
        message = self.get_object()
        action_type = request.POST.get('action')
        
        if action_type == 'mark_read':
            message.is_read = True
            message.save()
            messages.success(request, 'Message marked as read.')
        elif action_type == 'mark_unread':
            message.is_read = False
            message.save()
            messages.success(request, 'Message marked as unread.')
        elif action_type == 'responded':
            message.responded_at = timezone.now()
            message.save()
            messages.success(request, 'Message marked as responded.')
        
        return redirect('dashboard:contact_message_detail', pk=message.pk)


class AuditLogListView(AdminRoleMixin, ListView):
    """List all audit logs."""
    
    model = AuditLog
    template_name = 'dashboard/audit_log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('actor').order_by('-created_at')
        
        # Filter by action
        action = self.request.GET.get('action', '')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_filter'] = self.request.GET.get('action', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Get unique actions for filter dropdown
        context['available_actions'] = AuditLog.objects.values_list(
            'action', flat=True
        ).distinct().order_by('action')
        
        return context
