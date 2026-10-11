"""Filters for job applications."""
import django_filters
from django import forms
from .models import Application


class ApplicationFilterSet(django_filters.FilterSet):
    """Filter set for applications list."""
    
    status = django_filters.ChoiceFilter(
        choices=Application.STATUS_CHOICES,
        empty_label='All Statuses',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    job = django_filters.CharFilter(
        field_name='job__title',
        lookup_expr='icontains',
        label='Job Title',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by job title...'
        })
    )
    
    applied_after = django_filters.DateFilter(
        field_name='applied_at',
        lookup_expr='gte',
        label='Applied After',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    applied_before = django_filters.DateFilter(
        field_name='applied_at',
        lookup_expr='lte',
        label='Applied Before',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = Application
        fields = ['status', 'job', 'applied_after', 'applied_before']


class ApplicantFilterSet(django_filters.FilterSet):
    """Filter set for employee applicant management."""
    
    status = django_filters.ChoiceFilter(
        choices=Application.STATUS_CHOICES,
        empty_label='All Statuses',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='exact',
        label='Rating',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 5,
            'placeholder': 'Filter by rating (1-5)'
        })
    )
    
    applied_at__gte = django_filters.DateFilter(
        field_name='applied_at',
        lookup_expr='gte',
        label='Applied From',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    applied_at__lte = django_filters.DateFilter(
        field_name='applied_at',
        lookup_expr='lte',
        label='Applied To',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    job = django_filters.ModelChoiceFilter(
        queryset=None,
        label='Job',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Jobs'
    )
    
    class Meta:
        model = Application
        fields = ['status', 'rating', 'applied_at__gte', 'applied_at__lte', 'job']
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            from jobs.models import Job
            self.filters['job'].queryset = Job.objects.filter(company=company)
