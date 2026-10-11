from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import User, JobSeekerProfile, Education, Experience


class UserRegistrationForm(UserCreationForm):
    """Form for user registration with role selection."""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2']
        widgets = {
            'role': forms.RadioSelect(choices=[
                (User.USER, 'Job Seeker'),
                (User.EMPLOYEE, 'Recruiter'),
            ]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit role choices to USER and EMPLOYEE for public registration
        self.fields['role'].choices = [
            (User.USER, 'Job Seeker'),
            (User.EMPLOYEE, 'Recruiter'),
        ]
        # Make phone optional
        self.fields['phone'].required = False
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'role':
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserLoginForm(AuthenticationForm):
    """Form for user login."""
    
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with Bootstrap styling."""
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with Bootstrap styling."""
    
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )


class JobSeekerProfileForm(forms.ModelForm):
    """Form for job seeker profile."""
    
    class Meta:
        model = JobSeekerProfile
        fields = ['headline', 'bio', 'location', 'phone', 'avatar']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EducationForm(forms.ModelForm):
    """Form for education entries."""
    
    class Meta:
        model = Education
        fields = ['degree', 'field_of_study', 'institution', 'start_date', 'end_date', 'description']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ExperienceForm(forms.ModelForm):
    """Form for experience entries."""
    
    class Meta:
        model = Experience
        fields = ['title', 'company_name', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        """Validate that end_date is cleared if is_current is True."""
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        
        if is_current and end_date:
            cleaned_data['end_date'] = None
        
        return cleaned_data


class ResumeUploadForm(forms.ModelForm):
    """Form for resume upload with validation."""
    
    class Meta:
        model = JobSeekerProfile
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_resume(self):
        """Validate resume file size and type."""
        resume = self.cleaned_data.get('resume')
        
        if resume:
            # Check file size
            max_size = settings.MAX_RESUME_SIZE_MB * 1024 * 1024  # Convert to bytes
            if resume.size > max_size:
                raise ValidationError(
                    f'Resume file size must not exceed {settings.MAX_RESUME_SIZE_MB}MB.'
                )
            
            # Check file type
            if resume.content_type not in settings.ALLOWED_RESUME_TYPES:
                raise ValidationError(
                    'Resume must be a PDF, DOC, or DOCX file.'
                )
        
        return resume
