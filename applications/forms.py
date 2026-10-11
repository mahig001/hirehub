"""Forms for job applications."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import Application, Interview


class ApplicationForm(forms.ModelForm):
    """Form for submitting a job application."""
    
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Tell the employer why you are a good fit for this position...'
            })
        }
        labels = {
            'cover_letter': 'Cover Letter (Optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('cover_letter'),
            Div(
                Submit('submit', 'Submit Application', css_class='btn btn-primary btn-lg'),
                css_class='d-grid gap-2'
            )
        )


class InterviewForm(forms.ModelForm):
    """Form for scheduling an interview."""
    
    class Meta:
        model = Interview
        fields = ['scheduled_at', 'interview_type', 'location', 'notes', 'interviewer']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'interview_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter meeting room, address, or video call link...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional notes about the interview...'
            }),
            'interviewer': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('scheduled_at'),
            Field('interview_type'),
            Field('location'),
            Field('notes'),
            Field('interviewer'),
            Div(
                Submit('submit', 'Schedule Interview', css_class='btn btn-primary'),
                css_class='mt-3'
            )
        )
