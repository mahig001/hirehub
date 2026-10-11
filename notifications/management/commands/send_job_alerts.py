from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notifications.models import JobAlert
from jobs.models import Job
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Send job alerts to users based on their alert preferences'
    
    def handle(self, *args, **options):
        """Process active job alerts and send emails for matching jobs."""
        
        # Get all active job alerts
        active_alerts = JobAlert.objects.filter(is_active=True)
        
        alerts_processed = 0
        emails_sent = 0
        
        for alert in active_alerts:
            try:
                # Calculate the time window for new jobs
                if alert.last_sent_at:
                    since = alert.last_sent_at
                else:
                    # If never sent, look back 24 hours
                    since = timezone.now() - timedelta(hours=24)
                
                # Build query for matching jobs
                jobs_query = Job.objects.filter(
                    is_active=True,
                    is_approved=True,
                    posted_at__gte=since
                )
                
                # Filter by category if specified
                if alert.category:
                    jobs_query = jobs_query.filter(category=alert.category)
                
                # Filter by keywords if specified
                if alert.keywords:
                    keywords = [kw.strip() for kw in alert.keywords.split(',')]
                    from django.db.models import Q
                    keyword_query = Q()
                    for keyword in keywords:
                        if keyword:
                            keyword_query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
                    if keyword_query:
                        jobs_query = jobs_query.filter(keyword_query)
                
                # Filter by location if specified
                if alert.location:
                    jobs_query = jobs_query.filter(location__icontains=alert.location)
                
                # Filter by job type if specified
                if alert.job_type:
                    jobs_query = jobs_query.filter(job_type=alert.job_type)
                
                # Get matching jobs
                matching_jobs = jobs_query.distinct()
                
                # Send email if there are matching jobs
                if matching_jobs.exists():
                    success = NotificationService.send_email_notification(
                        recipient=alert.user,
                        subject=f'New Jobs Matching Your Alert - {matching_jobs.count()} job(s)',
                        template_name='notifications/emails/job_alert_email.html',
                        context={
                            'user_name': alert.user.get_full_name(),
                            'jobs': matching_jobs,
                        }
                    )
                    
                    if success:
                        emails_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Sent alert to {alert.user.email} - {matching_jobs.count()} jobs'
                            )
                        )
                
                # Update last_sent_at
                alert.last_sent_at = timezone.now()
                alert.save()
                
                alerts_processed += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing alert {alert.id}: {e}'
                    )
                )
        
        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: Processed {alerts_processed} alerts, sent {emails_sent} emails'
            )
        )
