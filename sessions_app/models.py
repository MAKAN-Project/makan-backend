from django.db import models
from users.models import User
from engineers.models import Engineer


class Session(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('reschedule_requested', 'Reschedule Requested'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    session_id = models.AutoField(primary_key=True)
    scheduled_at = models.DateTimeField()

    # روابط Zoom
    meeting_link = models.URLField(max_length=500, null=True, blank=True)  # join_url (للعميل)
    host_link = models.URLField(max_length=500, null=True, blank=True)     # start_url (للمهندس)

    # علاقات
    eng = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # بيانات إضافية
    old_scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=45, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.session_id} with {self.eng.user.first_name}"
