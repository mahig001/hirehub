from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from jobs.models import Category, Job
from .models import JobAlert


class JobAlertForm(forms.ModelForm):
    """Form for creating and updating job alerts."""
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Categories'
    )
    
    keywords = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, Django, Developer'
        }),
        help_text='Comma-separated keywords to search for'
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., New York, Remote'
        })
    )
    
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    frequency = forms.ChoiceField(
        choices=JobAlert.FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = JobAlert
        fields = ['category', 'keywords', 'location', 'job_type', 'frequency']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('category', css_class='col-md-6'),
                Column('job_type', css_class='col-md-6'),
            ),
            Row(
                Column('keywords', css_class='col-md-6'),
                Column('location', css_class='col-md-6'),
            ),
            'frequency',
            Submit('submit', 'Save Job Alert', css_class='btn btn-primary')
        )
