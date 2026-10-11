from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse
from .models import Notification, JobAlert
from .forms import JobAlertForm
from .services import NotificationService


class NotificationListView(LoginRequiredMixin, ListView):
    """List view for user notifications."""
    
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')


class MarkNotificationReadView(LoginRequiredMixin, View):
    """View to mark a notification as read."""
    
    def post(self, request, pk):
        """Mark notification as read."""
        success = NotificationService.mark_as_read(pk, request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': success})
        
        if success:
            messages.success(request, 'Notification marked as read.')
        else:
            messages.error(request, 'Failed to mark notification as read.')
        
        return redirect('notifications:list')


class MarkAllReadView(LoginRequiredMixin, View):
    """View to mark all notifications as read."""
    
    def post(self, request):
        """Mark all user's notifications as read."""
        count = NotificationService.mark_all_as_read(request.user)
        messages.success(request, f'Marked {count} notifications as read.')
        return redirect('notifications:list')


class JobAlertListView(LoginRequiredMixin, ListView):
    """List view for user's job alerts."""
    
    model = JobAlert
    template_name = 'notifications/job_alert_list.html'
    context_object_name = 'job_alerts'
    
    def get_queryset(self):
        """Return job alerts for the current user."""
        return JobAlert.objects.filter(user=self.request.user)


class JobAlertCreateView(LoginRequiredMixin, CreateView):
    """Create view for job alerts."""
    
    model = JobAlert
    form_class = JobAlertForm
    template_name = 'notifications/job_alert_form.html'
    success_url = reverse_lazy('notifications:alert_list')
    
    def form_valid(self, form):
        """Set the user before saving."""
        form.instance.user = self.request.user
        messages.success(self.request, 'Job alert created successfully.')
        return super().form_valid(form)


class JobAlertUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for job alerts."""
    
    model = JobAlert
    form_class = JobAlertForm
    template_name = 'notifications/job_alert_form.html'
    success_url = reverse_lazy('notifications:alert_list')
    
    def get_queryset(self):
        """Ensure users can only edit their own job alerts."""
        return JobAlert.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        """Add success message."""
        messages.success(self.request, 'Job alert updated successfully.')
        return super().form_valid(form)


class JobAlertDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for job alerts."""
    
    model = JobAlert
    template_name = 'notifications/job_alert_confirm_delete.html'
    success_url = reverse_lazy('notifications:alert_list')
    
    def get_queryset(self):
        """Ensure users can only delete their own job alerts."""
        return JobAlert.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Add success message."""
        messages.success(request, 'Job alert deleted successfully.')
        return super().delete(request, *args, **kwargs)


class JobAlertToggleView(LoginRequiredMixin, View):
    """View to toggle job alert active status."""
    
    def post(self, request, pk):
        """Toggle the is_active status."""
        job_alert = get_object_or_404(JobAlert, pk=pk, user=request.user)
        job_alert.is_active = not job_alert.is_active
        job_alert.save()
        
        status = 'activated' if job_alert.is_active else 'deactivated'
        messages.success(request, f'Job alert {status} successfully.')
        
        return redirect('notifications:alert_list')
