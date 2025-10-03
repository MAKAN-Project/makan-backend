from django.db import models
from users.models import User
from django.core.exceptions import ValidationError

# 🔹 Validator لحجم الصور (5MB max)
def validate_image(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("Image size must not exceed 5MB")

# 🔹 Validator لحجم الملفات (10MB max)
def validate_file(file):
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError("File size must not exceed 10MB")


class Engineer(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    eng_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="engineer_profile")

    education = models.CharField(max_length=255)
    certifications = models.CharField(max_length=255, blank=True, null=True)
    licenses = models.CharField(max_length=255, blank=True, null=True)

    profile_photo = models.ImageField(
        upload_to="engineers/photos/",
        blank=True,
        null=True,
        validators=[validate_image]
    )
    portfolio = models.FileField(
        upload_to="engineers/portfolio/",
        blank=True,
        null=True,
        validators=[validate_file]
    )

    bio = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'engineers'

    def __str__(self):
        return f"Engineer {self.user.first_name} {self.user.last_name}"
