from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileUpdateForm,
    CustomPasswordResetForm, CustomSetPasswordForm
)
from .models import User
import logging

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
