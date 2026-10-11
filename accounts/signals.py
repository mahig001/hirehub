from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeekerProfile


@receiver(post_save, sender=User)
def create_job_seeker_profile(sender, instance, created, **kwargs):
    """Auto-create JobSeekerProfile for USER role."""
    if created and instance.role == User.USER:
        JobSeekerProfile.objects.get_or_create(user=instance)
