from django.db import models
from users.models import User


class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=45)
    file_name = models.CharField(max_length=45)
    file = models.FileField(upload_to='uploads', null=True, blank=True)
    path = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='file')
    project_request = models.ForeignKey('projectrequests.ProjectRequest', on_delete=models.CASCADE, related_name='files', null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'files'

    def __str__(self):
        return self.file_name
