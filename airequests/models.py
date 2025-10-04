from django.db import models
from users.models import User

class AIRequest(models.Model):
    ai_request_id = models.AutoField(primary_key=True)
    input_image_path = models.CharField(max_length=255)
    style = models.CharField(max_length=45)
    output_images_paths = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='airequest')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'airequestes'

    def __str__(self):
        return f"AI Request {self.ai_request_id}"
