from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View, UpdateView, DeleteView, CreateView, ListView
from django.urls import reverse_lazy
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse, HttpResponseForbidden
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileUpdateForm,
    CustomPasswordResetForm, CustomSetPasswordForm,
    JobSeekerProfileForm, EducationForm, ExperienceForm, ResumeUploadForm
)
from .models import User, JobSeekerProfile, Education, Experience
import logging
import os

logger = logging.getLogger(__name__)


class RegisterView(View):
    """User registration view."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.is_email_verified = False
            user.save()
            
            # Send verification email
            self.send_verification_email(user, request)
            
            messages.success(
                request,
                'Registration successful! Please check your email to verify your account.'
            )
            logger.info(f'New user registered: {user.email} with role {user.role}')
            return redirect('accounts:login')
        
        return render(request, 'accounts/register.html', {'form': form})
    
    def send_verification_email(self, user, request):
        """Send email verification link."""
        signer = Signer()
        token = signer.sign(user.email)
        
        verify_url = request.build_absolute_uri(
            f'/accounts/verify/{token}/'
        )
        
        subject = 'Verify Your Email - HireHub'
        message = render_to_string('accounts/emails/verification_email.html', {
            'user': user,
            'verify_url': verify_url,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class LoginView(View):
    """User login view."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)
                
                # Redirect to dashboard based on role
                next_url = request.GET.get('next') or user.get_dashboard_url()
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                logger.info(f'User logged in: {user.email}')
                return redirect(next_url)
        
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(LoginRequiredMixin, View):
    """User logout view."""
    
    def get(self, request):
        return render(request, 'accounts/logout_confirm.html')
    
    def post(self, request):
        logger.info(f'User logged out: {request.user.email}')
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('core:home')


class VerifyEmailView(View):
    """Email verification view."""
    
    def get(self, request, token):
        signer = Signer()
        try:
            email = signer.unsign(token)
            user = get_object_or_404(User, email=email)
            
            if user.is_email_verified:
                messages.info(request, 'Your email is already verified.')
            else:
                user.is_email_verified = True
                user.save()
                messages.success(request, 'Your email has been verified successfully!')
                logger.info(f'Email verified for user: {user.email}')
            
            return redirect('accounts:login')
        
        except (BadSignature, User.DoesNotExist):
            messages.error(request, 'Invalid or expired verification link.')
            return redirect('accounts:login')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """User profile update view."""
    
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    """User account deletion view."""
    
    model = User
    template_name = 'accounts/account_delete_confirm.html'
    success_url = reverse_lazy('core:home')
    
    def get_object(self):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        logger.warning(f'User account deleted: {user.email}')
        messages.success(request, 'Your account has been deleted.')
        return super().delete(request, *args, **kwargs)


# Password reset views with custom templates
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'


# Job Seeker Profile Views

class ProfileDetailView(LoginRequiredMixin, View):
    """View job seeker profile with completeness meter."""
    
    def get(self, request):
        # Get or create job seeker profile
        profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
        
        # Get education and experience
        education_list = request.user.education_set.all()
        experience_list = request.user.experience_set.all()
        
        # Calculate completeness
        completeness = profile.calculate_completeness()
        
        context = {
            'profile': profile,
            'education_list': education_list,
            'experience_list': experience_list,
            'completeness': completeness,
        }
        return render(request, 'accounts/profile_detail.html', context)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit job seeker profile."""
    
    model = JobSeekerProfile
    form_class = JobSeekerProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def get_object(self):
        profile, created = JobSeekerProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        logger.info(f'Profile updated for user: {self.request.user.email}')
        return super().form_valid(form)


class ResumeUploadView(LoginRequiredMixin, UpdateView):
    """Upload resume to private storage."""
    
    model = JobSeekerProfile
    form_class = ResumeUploadForm
    template_name = 'accounts/resume_upload.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def get_object(self):
        profile, created = JobSeekerProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Resume uploaded successfully!')
        logger.info(f'Resume uploaded for user: {self.request.user.email}')
        return super().form_valid(form)


class ResumeDownloadView(LoginRequiredMixin, View):
    """Download resume with permission check."""
    
    def get(self, request, user_id):
        # Get the profile
        profile = get_object_or_404(JobSeekerProfile, user_id=user_id)
        
        # Check permissions: owner or recruiter viewing application
        if request.user.id == user_id:
            # User viewing their own resume
            pass
        elif request.user.role == User.EMPLOYEE:
            # Recruiter can view resumes of applicants
            # TODO: Add check if recruiter has application from this user
            pass
        else:
            logger.warning(
                f'Unauthorized resume access attempt by {request.user.email} '
                f'for user {user_id}'
            )
            return HttpResponseForbidden('You do not have permission to view this resume.')
        
        # Check if resume exists
        if not profile.resume:
            raise Http404('Resume not found.')
        
        # Serve the file
        try:
            response = FileResponse(profile.resume.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(profile.resume.name)}"'
            logger.info(f'Resume downloaded: {profile.resume.name} by {request.user.email}')
            return response
        except FileNotFoundError:
            raise Http404('Resume file not found.')


# Education CRUD Views

class EducationCreateView(LoginRequiredMixin, CreateView):
    """Create education entry."""
    
    model = Education
    form_class = EducationForm
    template_name = 'accounts/education_form.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Education added successfully!')
        logger.info(f'Education added for user: {self.request.user.email}')
        return super().form_valid(form)


class EducationUpdateView(LoginRequiredMixin, UpdateView):
    """Update education entry."""
    
    model = Education
    form_class = EducationForm
    template_name = 'accounts/education_form.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def get_queryset(self):
        # Only allow users to edit their own education
        return Education.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Education updated successfully!')
        return super().form_valid(form)


class EducationDeleteView(LoginRequiredMixin, DeleteView):
    """Delete education entry."""
    
    model = Education
    template_name = 'accounts/education_confirm_delete.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def get_queryset(self):
        # Only allow users to delete their own education
        return Education.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Education deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Experience CRUD Views

class ExperienceCreateView(LoginRequiredMixin, CreateView):
    """Create experience entry."""
    
    model = Experience
    form_class = ExperienceForm
    template_name = 'accounts/experience_form.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Experience added successfully!')
        logger.info(f'Experience added for user: {self.request.user.email}')
        return super().form_valid(form)


class ExperienceUpdateView(LoginRequiredMixin, UpdateView):
    """Update experience entry."""
    
    model = Experience
    form_class = ExperienceForm
    template_name = 'accounts/experience_form.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def get_queryset(self):
        # Only allow users to edit their own experience
        return Experience.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Experience updated successfully!')
        return super().form_valid(form)


class ExperienceDeleteView(LoginRequiredMixin, DeleteView):
    """Delete experience entry."""
    
    model = Experience
    template_name = 'accounts/experience_confirm_delete.html'
    success_url = reverse_lazy('accounts:profile_detail')
    
    def get_queryset(self):
        # Only allow users to delete their own experience
        return Experience.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Experience deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Saved Jobs Views

class SavedJobsListView(LoginRequiredMixin, ListView):
    """List user's saved jobs."""
    
    model = JobSeekerProfile
    template_name = 'accounts/saved_jobs.html'
    context_object_name = 'saved_jobs'
    
    def get_queryset(self):
        profile, created = JobSeekerProfile.objects.get_or_create(user=self.request.user)
        return profile.saved_jobs.all()


@login_required
def toggle_saved_job(request, pk):
    """Toggle saved job (add/remove from saved_jobs M2M)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    # Import here to avoid circular import
    from jobs.models import Job
    
    job = get_object_or_404(Job, pk=pk)
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    
    if job in profile.saved_jobs.all():
        profile.saved_jobs.remove(job)
        saved = False
        message = 'Job removed from saved jobs.'
    else:
        profile.saved_jobs.add(job)
        saved = True
        message = 'Job saved successfully!'
    
    logger.info(f'User {request.user.email} {"saved" if saved else "unsaved"} job {job.id}')
    
    return JsonResponse({
        'saved': saved,
        'message': message
    })
