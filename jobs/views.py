from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView, ListView, FormView
from django.urls import reverse_lazy
from django.conf import settings
from django_filters.views import FilterView
from .models import Job, JobReport
from .forms import JobForm, JobFilterSet, ReportJobForm
from accounts.models import User
from companies.models import Employee
import logging

logger = logging.getLogger(__name__)


class JobCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new job (EMPLOYEE role only with company)."""
    
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is EMPLOYEE and has a company."""
        if request.user.role != User.EMPLOYEE:
            messages.error(request, 'Only recruiters can post jobs.')
            return redirect('core:home')
        
        # Check if user is company owner or employee
        if not hasattr(request.user, 'company') and not request.user.employments.exists():
            messages.error(request, 'You must be associated with a company to post jobs.')
            return redirect('companies:create')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Set the company and approval status."""
        # Get company (owner's company or first employment)
        if hasattr(self.request.user, 'company'):
            form.instance.company = self.request.user.company
        else:
            # Get first employment's company
            employment = self.request.user.employments.first()
            if employment:
                form.instance.company = employment.company
            else:
                messages.error(self.request, 'You must be associated with a company to post jobs.')
                return redirect('companies:create')
        
        # Set approval based on JOB_MODERATION_ENABLED setting
        if not settings.JOB_MODERATION_ENABLED:
            form.instance.is_approved = True
        
        response = super().form_valid(form)
        
        if settings.JOB_MODERATION_ENABLED:
            messages.success(
                self.request,
                'Job posted successfully! It will be reviewed by our team before going live.'
            )
        else:
            messages.success(self.request, 'Job posted successfully!')
        
        logger.info(f'Job created: {form.instance.title} by {self.request.user.email}')
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class JobUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a job (company owner/employees only)."""
    
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user can edit this job."""
        job = self.get_object()
        
        # Check if user is company owner or employee
        is_owner = hasattr(request.user, 'company') and job.company == request.user.company
        is_employee = Employee.objects.filter(user=request.user, company=job.company).exists()
        
        if not (is_owner or is_employee):
            messages.error(request, 'You do not have permission to edit this job.')
            return redirect('jobs:detail', slug=job.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, 'Job updated successfully!')
        logger.info(f'Job updated: {form.instance.title} by {self.request.user.email}')
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class JobDetailView(DetailView):
    """Public view for job details."""
    
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        """Add permissions to context."""
        context = super().get_context_data(**kwargs)
        job = self.object
        user = self.request.user
        
        # Check if user can edit
        can_edit = False
        if user.is_authenticated:
            is_owner = hasattr(user, 'company') and job.company == user.company
            is_employee = Employee.objects.filter(user=user, company=job.company).exists()
            can_edit = is_owner or is_employee
        
        context['can_edit'] = can_edit
        context['is_job_seeker'] = user.is_authenticated and user.role == User.USER
        
        # Check if user has already applied
        if user.is_authenticated and user.role == User.USER:
            from applications.models import Application
            try:
                user_application = Application.objects.get(job=job, applicant=user)
                context['user_application'] = user_application
            except Application.DoesNotExist:
                context['user_application'] = None
        
        return context


class JobListView(FilterView):
    """Public view for listing jobs with filters."""
    
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    filterset_class = JobFilterSet
    paginate_by = settings.JOBS_PER_PAGE
    
    def get_queryset(self):
        """Return active jobs (approved if moderation enabled)."""
        queryset = Job.objects.filter(is_active=True).select_related('company', 'category')
        
        if settings.JOB_MODERATION_ENABLED:
            queryset = queryset.filter(is_approved=True)
        
        return queryset.order_by('-posted_at')


class MyJobsListView(LoginRequiredMixin, ListView):
    """View for listing jobs posted by user's company."""
    
    model = Job
    template_name = 'jobs/my_jobs.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is EMPLOYEE with a company."""
        if request.user.role != User.EMPLOYEE:
            messages.error(request, 'Only recruiters can access this page.')
            return redirect('core:home')
        
        # Get user's companies (owner or employee)
        self.companies = []
        if hasattr(request.user, 'company'):
            self.companies.append(request.user.company)
        
        # Add companies where user is an employee
        employments = request.user.employments.select_related('company')
        for employment in employments:
            if employment.company not in self.companies:
                self.companies.append(employment.company)
        
        if not self.companies:
            messages.error(request, 'You must be associated with a company.')
            return redirect('companies:create')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Return jobs from user's companies."""
        return Job.objects.filter(
            company__in=self.companies
        ).select_related('company', 'category').order_by('-posted_at')
    
    def get_context_data(self, **kwargs):
        """Add companies to context."""
        context = super().get_context_data(**kwargs)
        context['companies'] = self.companies
        return context


class ReportJobView(LoginRequiredMixin, FormView):
    """View for reporting a job."""
    
    template_name = 'jobs/report_job.html'
    form_class = ReportJobForm
    
    def dispatch(self, request, *args, **kwargs):
        """Get the job being reported."""
        self.job = get_object_or_404(Job, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add job to context."""
        context = super().get_context_data(**kwargs)
        context['job'] = self.job
        return context
    
    def form_valid(self, form):
        """Create the job report."""
        JobReport.objects.create(
            job=self.job,
            reporter=self.request.user,
            reason=form.cleaned_data['reason'],
            description=form.cleaned_data['description']
        )
        messages.success(
            self.request,
            'Thank you for reporting this job. We will review it shortly.'
        )
        logger.info(f'Job reported: {self.job.title} by {self.request.user.email}')
        return redirect('jobs:detail', slug=self.job.slug)
    
    def get_success_url(self):
        return reverse_lazy('jobs:detail', kwargs={'slug': self.job.slug})
