from django.db import models
from users.models import User
from category.models import Category
from django.utils.text import slugify
from django.utils import timezone

def model3d_upload_path(instance, filename):
    # مسار حفظ فريد لكل موديل
    safe_name = slugify(instance.name)
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f"models3d/{safe_name}_{timestamp}/{filename}"

class Model3D(models.Model):
    model_id = models.AutoField(db_column='3d_model_id', primary_key=True)
    name = models.CharField(max_length=100)
    model_file = models.FileField(upload_to=model3d_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = '3d_models'

    def __str__(self):
        return self.name

    @property
    def model_url(self):
        return self.model_file.url
