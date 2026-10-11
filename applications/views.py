"""Views for job applications."""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, ListView, View
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from django_filters.views import FilterView
from jobs.models import Job
from companies.models import Company
from .models import Application, ApplicationStatusHistory
from .forms import ApplicationForm
from .filters import ApplicationFilterSet
from .services import ApplicationService

logger = logging.getLogger(__name__)


class ApplyView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for job seekers to apply to a job."""
    
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/apply_form.html'
    
    def test_func(self):
        """Only job seekers (USER role) can apply."""
        return self.request.user.role == 'USER'
    
    def get_job(self):
        """Get the job being applied to."""
        return get_object_or_404(Job, pk=self.kwargs['job_pk'], is_active=True)
    
    def get_context_data(self, **kwargs):
        """Add job to context."""
        context = super().get_context_data(**kwargs)
        context['job'] = self.get_job()
        return context
    
    def form_valid(self, form):
        """Create application using service."""
        job = self.get_job()
        
        try:
            application = ApplicationService.create_application(
                job=job,
                applicant=self.request.user,
                cover_letter=form.cleaned_data.get('cover_letter', '')
            )
            messages.success(
                self.request,
                f'Your application to {job.title} has been submitted successfully!'
            )
            logger.info(f'User {self.request.user.email} applied to job {job.id}')
            return redirect('applications:detail', pk=application.pk)
        
        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect('jobs:detail', slug=job.slug)
    
    def handle_no_permission(self):
        """Redirect non-job-seekers with error message."""
        messages.error(self.request, 'Only job seekers can apply to jobs.')
        return redirect('core:home')


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """View for viewing application details."""
    
    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'
    
    def get_queryset(self):
        """Filter applications based on user role."""
        user = self.request.user
        
        if user.role == 'USER':
            # Job seekers can only view their own applications
            return Application.objects.filter(applicant=user).select_related('job', 'job__company')
        
        elif user.role == 'EMPLOYEE':
            # Recruiters can view applications for their company's jobs
            try:
                company = user.company
                return Application.objects.filter(job__company=company).select_related('job', 'applicant')
            except Company.DoesNotExist:
                return Application.objects.none()
        
        elif user.role == 'ADMIN':
            # Admins can view all applications
            return Application.objects.all().select_related('job', 'applicant')
        
        return Application.objects.none()
    
    def get_context_data(self, **kwargs):
        """Add status history to context."""
        context = super().get_context_data(**kwargs)
        context['status_history'] = ApplicationService.get_status_history(self.object)
        return context


class MyApplicationsListView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    """View for job seekers to see their applications."""
    
    model = Application
    template_name = 'applications/my_applications.html'
    context_object_name = 'applications'
    filterset_class = ApplicationFilterSet
    paginate_by = 20
    
    def test_func(self):
        """Only job seekers (USER role) can view this."""
        return self.request.user.role == 'USER'
    
    def get_queryset(self):
        """Get applications for current user."""
        return Application.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__company').order_by('-applied_at')
    
    def handle_no_permission(self):
        """Redirect non-job-seekers with error message."""
        messages.error(self.request, 'Only job seekers can view applications.')
        return redirect('core:home')


class WithdrawApplicationView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for job seekers to withdraw their application."""
    
    def test_func(self):
        """Only job seekers can withdraw applications."""
        return self.request.user.role == 'USER'
    
    def post(self, request, pk):
        """Withdraw the application."""
        application = get_object_or_404(Application, pk=pk, applicant=request.user)
        
        try:
            ApplicationService.withdraw_application(application, request.user)
            messages.success(request, 'Your application has been withdrawn.')
            logger.info(f'User {request.user.email} withdrew application {application.id}')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('applications:detail', pk=pk)
    
    def handle_no_permission(self):
        """Redirect non-job-seekers with error message."""
        messages.error(self.request, 'Only job seekers can withdraw applications.')
        return redirect('core:home')


class JobApplicantsListView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    """View for recruiters to see applicants for a job."""
    
    model = Application
    template_name = 'applications/applicants_list.html'
    context_object_name = 'applications'
    filterset_class = ApplicationFilterSet
    paginate_by = 20
    
    def test_func(self):
        """Only employees/recruiters can view this."""
        return self.request.user.role == 'EMPLOYEE'
    
    def get_job(self):
        """Get the job for which applicants are being viewed."""
        if not hasattr(self, '_job'):
            self._job = get_object_or_404(Job, pk=self.kwargs['pk'])
        return self._job
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to view this job's applicants."""
        job = self.get_job()
        
        try:
            company = request.user.company
            if job.company != company:
                raise PermissionDenied('You can only view applicants for your company\'s jobs.')
        except Company.DoesNotExist:
            raise PermissionDenied('You must be associated with a company to view applicants.')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Get applications for this job."""
        job = self.get_job()
        return Application.objects.filter(job=job).select_related('applicant').order_by('-applied_at')
    
    def get_context_data(self, **kwargs):
        """Add job to context."""
        context = super().get_context_data(**kwargs)
        context['job'] = self.get_job()
        return context
    
    def handle_no_permission(self):
        """Redirect non-recruiters with error message."""
        messages.error(self.request, 'Only recruiters can view job applicants.')
        return redirect('core:home')


class ApplicationStatusTimelineView(LoginRequiredMixin, DetailView):
    """View for displaying application status timeline (JSON response)."""
    
    model = Application
    
    def get_queryset(self):
        """Filter applications based on user role."""
        user = self.request.user
        
        if user.role == 'USER':
            return Application.objects.filter(applicant=user)
        elif user.role == 'EMPLOYEE':
            try:
                company = user.company
                return Application.objects.filter(job__company=company)
            except Company.DoesNotExist:
                return Application.objects.none()
        elif user.role == 'ADMIN':
            return Application.objects.all()
        
        return Application.objects.none()
    
    def get(self, request, *args, **kwargs):
        """Return timeline as JSON."""
        application = self.get_object()
        history = ApplicationService.get_status_history(application)
        
        timeline_data = [
            {
                'old_status': h.old_status,
                'new_status': h.new_status,
                'changed_by': h.changed_by.get_full_name() if h.changed_by else 'System',
                'changed_at': h.changed_at.isoformat(),
                'note': h.note
            }
            for h in history
        ]
        
        return JsonResponse({'timeline': timeline_data})
