from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from django_filters import FilterSet, CharFilter, MultipleChoiceFilter, ModelChoiceFilter, ModelMultipleChoiceFilter
from .models import Job, Category, Skill


class JobForm(forms.ModelForm):
    """Form for creating and updating jobs."""
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'category', 'skills', 'location',
            'job_type', 'salary_min', 'salary_max', 'deadline', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Describe the job responsibilities, requirements, and qualifications...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'skills': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '8'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country or Remote'
            }),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary',
                'step': '1000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary',
                'step': '1000'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['salary_min'].required = False
        self.fields['salary_max'].required = False
        self.fields['deadline'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('title'),
            Field('description'),
            Row(
                Column('category', css_class='col-md-6'),
                Column('job_type', css_class='col-md-6'),
            ),
            Field('skills', css_class='mb-3'),
            Field('location'),
            Row(
                Column('salary_min', css_class='col-md-6'),
                Column('salary_max', css_class='col-md-6'),
            ),
            Field('deadline'),
            Field('is_active'),
            Submit('submit', 'Save Job', css_class='btn btn-primary')
        )
    
    def clean(self):
        """Validate salary range."""
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data


class JobFilterSet(FilterSet):
    """Filter set for job listing page."""
    
    category = ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    skills = ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        conjoined=False,  # OR logic
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'})
    )
    
    location = CharFilter(
        field_name='location',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search location...'
        })
    )
    
    job_type = MultipleChoiceFilter(
        choices=Job.JOB_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Job
        fields = ['category', 'skills', 'location', 'job_type']


class ReportJobForm(forms.Form):
    """Form for reporting a job."""
    
    SPAM = 'SPAM'
    INAPPROPRIATE = 'INAPPROPRIATE'
    FRAUD = 'FRAUD'
    OTHER = 'OTHER'
    
    REASON_CHOICES = [
        ('', 'Select a reason...'),
        (SPAM, 'Spam'),
        (INAPPROPRIATE, 'Inappropriate'),
        (FRAUD, 'Fraud'),
        (OTHER, 'Other'),
    ]
    
    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Please provide details about why you are reporting this job...'
        })
    )
