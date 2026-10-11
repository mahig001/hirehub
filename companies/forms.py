from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Company, Employee
from accounts.models import User


class CompanyForm(forms.ModelForm):
    """Form for creating a new company."""
    
    class Meta:
        model = Company
        fields = ['name', 'logo', 'website', 'industry', 'size', 'location', 'about']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell us about your company...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('website', css_class='col-md-6'),
            ),
            Row(
                Column('industry', css_class='col-md-4'),
                Column('size', css_class='col-md-4'),
                Column('location', css_class='col-md-4'),
            ),
            Field('logo'),
            Field('about'),
            Submit('submit', 'Create Company', css_class='btn btn-primary')
        )


class CompanyUpdateForm(forms.ModelForm):
    """Form for updating an existing company."""
    
    class Meta:
        model = Company
        fields = ['name', 'logo', 'website', 'industry', 'size', 'location', 'about']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell us about your company...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('website', css_class='col-md-6'),
            ),
            Row(
                Column('industry', css_class='col-md-4'),
                Column('size', css_class='col-md-4'),
                Column('location', css_class='col-md-4'),
            ),
            Field('logo'),
            Field('about'),
            Submit('submit', 'Update Company', css_class='btn btn-primary')
        )


class EmployeeForm(forms.ModelForm):
    """Form for adding an employee to a company."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'employee@example.com'
        }),
        help_text='Enter the email of an existing user with EMPLOYEE role'
    )
    
    class Meta:
        model = Employee
        fields = ['position', 'is_primary']
        widgets = {
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., HR Manager, Recruiter'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('email'),
            Field('position'),
            Field('is_primary'),
            Submit('submit', 'Add Employee', css_class='btn btn-primary')
        )
    
    def clean_email(self):
        """Validate that the email belongs to an EMPLOYEE role user."""
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.role != User.EMPLOYEE:
                raise forms.ValidationError('This user is not registered as an employee/recruiter.')
            
            # Check if user is already an employee of this company
            if self.company and Employee.objects.filter(user=user, company=self.company).exists():
                raise forms.ValidationError('This user is already an employee of this company.')
            
            self.cleaned_data['user'] = user
            return email
        except User.DoesNotExist:
            raise forms.ValidationError('No user found with this email address.')
    
    def save(self, commit=True):
        """Override save to set the user from cleaned email."""
        instance = super().save(commit=False)
        instance.user = self.cleaned_data['user']
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
        return instance
