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
