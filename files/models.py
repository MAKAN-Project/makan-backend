from django.db import models
from users.models import User

class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=45)
    file_name = models.CharField(max_length=45)
    path = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'files'

    def __str__(self):
        return self.file_name
