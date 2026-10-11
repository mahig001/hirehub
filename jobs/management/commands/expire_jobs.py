from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import Job
from notifications.services import NotificationService
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Expire jobs that have passed their deadline'
    
    def handle(self, *args, **options):
        """Mark jobs as inactive if their deadline has passed."""
        
        today = timezone.now().date()
        
        # Find active jobs with past deadlines
        expired_jobs = Job.objects.filter(
            is_active=True,
            deadline__isnull=False,
            deadline__lt=today
        )
        
        expired_count = 0
        
        for job in expired_jobs:
            try:
                # Mark job as inactive
                job.is_active = False
                job.save()
                
                # Optionally notify job owner (company employees)
                company = job.company
                from companies.models import Employee
                employees = Employee.objects.filter(company=company).select_related('user')
                for employee in employees:
                    NotificationService.create_notification(
                        recipient=employee.user,
                        notification_type=Notification.JOB_ALERT,
                        title=f'Job Expired: {job.title}',
                        message=f'The job posting "{job.title}" has expired and is no longer active.',
                        link=f'/jobs/{job.slug}/'
                    )
                
                expired_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Expired job: {job.title} (deadline: {job.deadline})'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error expiring job {job.id}: {e}'
                    )
                )
        
        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {expired_count} jobs expired'
            )
        )
