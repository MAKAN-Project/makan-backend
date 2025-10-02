from django.db import models
from users.models import User
from category.models import Category

class Model3D(models.Model):
    model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = '3d_models'

    def __str__(self):
        return self.name
