from django.db import models
from users.models import User

class Engineer(models.Model):
    eng_id = models.AutoField(primary_key=True)
    education = models.CharField(max_length=45)
    certifications = models.CharField(max_length=45)
    licenses = models.CharField(max_length=45)
    profile_photo = models.CharField(max_length=255)
    portfolio = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=45)

    class Meta:
        db_table = 'engineers'

    def __str__(self):
        return f"Engineer {self.eng_id}"
