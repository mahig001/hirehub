from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Company, Employee
from .forms import CompanyForm, CompanyUpdateForm, EmployeeForm
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class CompanyCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new company (EMPLOYEE role only)."""
    
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is EMPLOYEE and doesn't have a company."""
        if request.user.role != User.EMPLOYEE:
            messages.error(request, 'Only users with recruiter role can create a company.')
            return redirect('core:home')
        
        if hasattr(request.user, 'company'):
            messages.info(request, 'You already have a company profile.')
            return redirect('companies:detail', slug=request.user.company.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Set the owner to the current user."""
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Company created successfully! It will be reviewed by our team.')
        logger.info(f'Company created: {form.instance.name} by {self.request.user.email}')
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating company (owner only)."""
    
    model = Company
    form_class = CompanyUpdateForm
    template_name = 'companies/company_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is the owner."""
        company = self.get_object()
        if company.owner != request.user:
            messages.error(request, 'You do not have permission to edit this company.')
            return redirect('companies:detail', slug=company.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, 'Company updated successfully!')
        logger.info(f'Company updated: {form.instance.name} by {self.request.user.email}')
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class CompanyDetailView(DetailView):
    """Public view for company details."""
    
    model = Company
    template_name = 'companies/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        """Add jobs to context."""
        context = super().get_context_data(**kwargs)
        company = self.object
        
        # Get active jobs (approved if moderation enabled)
        from django.conf import settings
        from jobs.models import Job
        
        jobs = Job.objects.filter(company=company, is_active=True)
        if settings.JOB_MODERATION_ENABLED:
            jobs = jobs.filter(is_approved=True)
        
        context['jobs'] = jobs.order_by('-posted_at')[:10]
        context['is_owner'] = self.request.user.is_authenticated and company.owner == self.request.user
        
        return context


class CompanyListView(ListView):
    """Public view for listing verified companies."""
    
    model = Company
    template_name = 'companies/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        """Return only verified companies."""
        queryset = Company.objects.filter(status=Company.VERIFIED)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(about__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """View for adding an employee to a company (owner only)."""
    
    model = Employee
    form_class = EmployeeForm
    template_name = 'companies/employee_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is company owner."""
        if not hasattr(request.user, 'company'):
            messages.error(request, 'You do not have a company.')
            return redirect('core:home')
        
        self.company = request.user.company
        if self.company.owner != request.user:
            messages.error(request, 'Only the company owner can add employees.')
            return redirect('companies:detail', slug=self.company.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Pass company to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.company
        return kwargs
    
    def form_valid(self, form):
        """Set the company."""
        form.instance.company = self.company
        response = super().form_valid(form)
        messages.success(self.request, f'Employee {form.instance.user.get_full_name()} added successfully!')
        logger.info(f'Employee added: {form.instance.user.email} to {self.company.name}')
        return response
    
    def get_success_url(self):
        return reverse_lazy('companies:employee_list')


class EmployeeListView(LoginRequiredMixin, ListView):
    """View for listing company employees (owner only)."""
    
    model = Employee
    template_name = 'companies/employee_list.html'
    context_object_name = 'employees'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is company owner."""
        if not hasattr(request.user, 'company'):
            messages.error(request, 'You do not have a company.')
            return redirect('core:home')
        
        self.company = request.user.company
        if self.company.owner != request.user:
            messages.error(request, 'Only the company owner can view employees.')
            return redirect('companies:detail', slug=self.company.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Return employees of the company."""
        return Employee.objects.filter(company=self.company).select_related('user')
    
    def get_context_data(self, **kwargs):
        """Add company to context."""
        context = super().get_context_data(**kwargs)
        context['company'] = self.company
        return context


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    """View for removing an employee from a company (owner only)."""
    
    model = Employee
    template_name = 'companies/employee_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check that user is company owner."""
        employee = self.get_object()
        if not hasattr(request.user, 'company'):
            messages.error(request, 'You do not have a company.')
            return redirect('core:home')
        
        if employee.company.owner != request.user:
            messages.error(request, 'Only the company owner can remove employees.')
            return redirect('companies:detail', slug=employee.company.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Employee removed successfully.')
        logger.info(f'Employee removed: {self.object.user.email} from {self.object.company.name}')
        return reverse_lazy('companies:employee_list')
