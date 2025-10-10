from django.db import models
from django.utils import timezone
from users.models import User  # هذا تمام — نحتاجه أكيد

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('project_request', 'Project Request'),
        ('accepted', 'Request Accepted'),
        ('rejected', 'Request Rejected'),
        ('in_progress', 'Project In Progress'),
        ('completed', 'Project Completed'),
        ('reschedule', 'Session Rescheduled'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications'
    )
    
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    message = models.TextField()

    # ✅ لاحظ هنا نستخدم أسماء النصوص بدل الاستيراد
    project_request = models.ForeignKey(
        'projectrequests.ProjectRequest',  # نص بدل import
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    session = models.ForeignKey(
        'sessions_app.Session',  # اسم التطبيق + الموديل
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"🔔 {self.type} → {self.recipient.first_name} {self.recipient.last_name}"
