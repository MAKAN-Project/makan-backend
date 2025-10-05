from django.contrib import admin
from .models import Model3D



@admin.register(Model3D)
class Model3DAdmin(admin.ModelAdmin):
    list_display = ('model_id', 'name', 'category', 'user', 'created_at')
    search_fields = ('name', 'category__category_name', 'user__first_name', 'user__last_name')
    list_filter = ('category', 'created_at')
