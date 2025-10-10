from django.db.models.signals import post_save
from django.dispatch import receiver
from projectrequests.models import ProjectRequest
from .utils import create_notification

@receiver(post_save, sender=ProjectRequest)
def notify_engineer_on_project_request(sender, instance, created, **kwargs):
    if created:
        create_notification(
            recipient=instance.engineer.user,
            sender=instance.client,
            notif_type='project_request',
            message=f"New project request from {instance.client.first_name} {instance.client.last_name}",
            project_request=instance
        )
