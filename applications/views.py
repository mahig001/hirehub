"""Views for job applications."""
import csv
import logging
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, ListView, View
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django_filters.views import FilterView
from jobs.models import Job
from companies.models import Company
from accounts.mixins import EmployeeRoleMixin
from .models import Application, ApplicationStatusHistory, Interview
from .forms import ApplicationForm, InterviewForm
from .filters import ApplicationFilterSet, ApplicantFilterSet
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


class JobApplicantsListView(EmployeeRoleMixin, FilterView):
    """View for recruiters to see applicants for a job."""
    
    model = Application
    template_name = 'applications/applicants_list.html'
    context_object_name = 'applications'
    filterset_class = ApplicantFilterSet
    paginate_by = 20
    
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
    
    def get_filterset_kwargs(self, *args, **kwargs):
        """Pass company to filterset."""
        kwargs = super().get_filterset_kwargs(*args, **kwargs)
        kwargs['company'] = self.request.user.company
        return kwargs
    
    def get_queryset(self):
        """Get applications for this job with sorting."""
        job = self.get_job()
        queryset = Application.objects.filter(job=job).select_related(
            'applicant', 'applicant__job_seeker_profile'
        )
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', 'date')
        if sort_by == 'rating':
            queryset = queryset.order_by('-rating', '-applied_at')
        elif sort_by == 'name':
            queryset = queryset.order_by('applicant__first_name', 'applicant__last_name')
        else:  # default: date
            queryset = queryset.order_by('-applied_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add job and sort parameter to context."""
        context = super().get_context_data(**kwargs)
        context['job'] = self.get_job()
        context['sort_by'] = self.request.GET.get('sort_by', 'date')
        return context


class ApplicantDetailView(EmployeeRoleMixin, DetailView):
    """View for recruiters to see applicant details."""
    
    model = Application
    template_name = 'applications/applicant_detail.html'
    context_object_name = 'application'
    
    def get_queryset(self):
        """Only show applications for user's company."""
        try:
            company = self.request.user.company
            return Application.objects.filter(job__company=company).select_related(
                'job', 'applicant', 'applicant__job_seeker_profile'
            ).prefetch_related('interviews')
        except Company.DoesNotExist:
            return Application.objects.none()
    
    def get_context_data(self, **kwargs):
        """Add interview form and related data to context."""
        context = super().get_context_data(**kwargs)
        context['status_history'] = ApplicationService.get_status_history(self.object)
        context['interviews'] = self.object.interviews.all().order_by('scheduled_at')
        context['interview_form'] = InterviewForm()
        context['status_choices'] = Application.STATUS_CHOICES
        return context


class ScheduleInterviewView(EmployeeRoleMixin, View):
    """View for recruiters to schedule an interview."""
    
    def post(self, request, pk):
        """Create interview via service."""
        application = get_object_or_404(
            Application.objects.select_related('job'),
            pk=pk,
            job__company=request.user.company
        )
        
        form = InterviewForm(request.POST)
        if form.is_valid():
            try:
                interview_data = {
                    'scheduled_at': form.cleaned_data['scheduled_at'],
                    'interview_type': form.cleaned_data['interview_type'],
                    'location': form.cleaned_data['location'],
                    'notes': form.cleaned_data.get('notes', ''),
                    'interviewer': form.cleaned_data.get('interviewer'),
                    'rating': None
                }
                ApplicationService.schedule_interview(application, interview_data, request.user)
                messages.success(request, 'Interview scheduled successfully.')
                logger.info(f'Interview scheduled for application {application.id} by {request.user.email}')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        return redirect('applications:applicant_detail', pk=pk)


class UpdateApplicantStatusView(EmployeeRoleMixin, View):
    """View for recruiters to update applicant status."""
    
    def post(self, request, pk):
        """Change status with note via ApplicationService."""
        application = get_object_or_404(
            Application,
            pk=pk,
            job__company=request.user.company
        )
        
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        
        try:
            ApplicationService.change_status(application, new_status, request.user, note)
            messages.success(request, f'Status updated to {application.get_status_display()}.')
            logger.info(f'Application {application.id} status updated by {request.user.email}')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('applications:applicant_detail', pk=pk)


class AddApplicantNoteView(EmployeeRoleMixin, View):
    """View for recruiters to add notes to applicant."""
    
    def post(self, request, pk):
        """Add note to recruiter_notes."""
        application = get_object_or_404(
            Application,
            pk=pk,
            job__company=request.user.company
        )
        
        note = request.POST.get('note', '').strip()
        if note:
            ApplicationService.add_applicant_note(application, note)
            messages.success(request, 'Note added successfully.')
            logger.info(f'Note added to application {application.id} by {request.user.email}')
        else:
            messages.error(request, 'Note cannot be empty.')
        
        return redirect('applications:applicant_detail', pk=pk)


class RateApplicantView(EmployeeRoleMixin, View):
    """View for recruiters to rate applicant."""
    
    def post(self, request, pk):
        """Set rating for applicant."""
        application = get_object_or_404(
            Application,
            pk=pk,
            job__company=request.user.company
        )
        
        try:
            rating = int(request.POST.get('rating', 0))
            ApplicationService.rate_applicant(application, rating)
            messages.success(request, f'Rating set to {rating} stars.')
            logger.info(f'Application {application.id} rated {rating} by {request.user.email}')
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
        
        return redirect('applications:applicant_detail', pk=pk)


class BulkActionView(EmployeeRoleMixin, View):
    """View for bulk status changes."""
    
    def post(self, request, job_pk):
        """Handle bulk status changes for a job's applicants."""
        job = get_object_or_404(Job, pk=job_pk, company=request.user.company)
        
        application_ids = request.POST.getlist('application_ids')
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        
        if not application_ids:
            messages.error(request, 'No applications selected.')
            return redirect('applications:job_applicants', pk=job_pk)
        
        # Verify all applications belong to this job
        applications = Application.objects.filter(
            id__in=application_ids,
            job=job
        )
        
        if applications.count() != len(application_ids):
            messages.error(request, 'Invalid application selection.')
            return redirect('applications:job_applicants', pk=job_pk)
        
        try:
            updated = ApplicationService.bulk_change_status(
                application_ids,
                action,
                request.user,
                note
            )
            messages.success(request, f'{len(updated)} applications updated to {action}.')
            logger.info(f'Bulk action: {len(updated)} applications updated to {action} by {request.user.email}')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('applications:job_applicants', pk=job_pk)


class ExportApplicantsCSVView(EmployeeRoleMixin, View):
    """View to export applicants to CSV."""
    
    def get(self, request, job_pk):
        """Generate CSV file."""
        job = get_object_or_404(Job, pk=job_pk, company=request.user.company)
        
        applications = Application.objects.filter(job=job).select_related(
            'applicant', 'applicant__job_seeker_profile'
        ).order_by('-applied_at')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="applicants_{job.slug}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Job Title', 'Status', 'Rating', 'Applied Date', 'Resume URL'])
        
        for app in applications:
            resume_url = ''
            try:
                if app.applicant.job_seeker_profile and app.applicant.job_seeker_profile.resume:
                    resume_url = request.build_absolute_uri(app.applicant.job_seeker_profile.resume.url)
            except:
                pass
            
            writer.writerow([
                app.applicant.get_full_name(),
                app.applicant.email,
                job.title,
                app.get_status_display(),
                app.rating or '',
                app.applied_at.strftime('%Y-%m-%d'),
                resume_url
            ])
        
        logger.info(f'CSV export for job {job.id} by {request.user.email}')
        return response


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
