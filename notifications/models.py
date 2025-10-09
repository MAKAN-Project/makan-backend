from django.db import models
from django.utils import timezone
from users.models import User
from projectrequests.models import ProjectRequest


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('request', 'New Project Request'),
        ('accepted', 'Request Accepted'),
        ('rejected', 'Request Rejected'),
        ('completed', 'Project Completed'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    project_request = models.ForeignKey(ProjectRequest, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.email} - {self.type}"

