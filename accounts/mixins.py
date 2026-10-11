from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to restrict access based on user role.
    Set allowed_roles in the view.
    """
    allowed_roles = []
    
    def test_func(self):
        return self.request.user.role in self.allowed_roles
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        messages.error(self.request, 'You do not have permission to access this page.')
        raise PermissionDenied


class UserRoleMixin(RoleRequiredMixin):
    """Mixin for job seeker (USER) views."""
    allowed_roles = ['USER']


class EmployeeRoleMixin(RoleRequiredMixin):
    """Mixin for recruiter (EMPLOYEE) views."""
    allowed_roles = ['EMPLOYEE']


class AdminRoleMixin(RoleRequiredMixin):
    """Mixin for admin (ADMIN) views."""
    allowed_roles = ['ADMIN']


class StaffOrAdminMixin(RoleRequiredMixin):
    """Mixin for staff or admin views."""
    allowed_roles = ['ADMIN']
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role == 'ADMIN'
