from django.db import models
from users.models import User
from engineers.models import Engineer
from files.models import File
from sessions_app.models import Session
from engineers.models import EngineerAvailability

class ProjectRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_requests')
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='project_requests')
    description = models.TextField()  # وصف الطلب (مثلاً: "أريد تصميم واجهة منزل")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.OneToOneField(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_request'
    )
    selected_availability = models.ForeignKey(
        EngineerAvailability,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests"
    )

    class Meta:
        db_table = 'project_requests'

    def __str__(self):
        return f"Request {self.request_id} - {self.client.first_name} {self.client.last_name}"
