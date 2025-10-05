from django.contrib import admin
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'file_name', 'type', 'user', 'created_at')
    search_fields = ('file_name', 'type', 'user__first_name', 'user__last_name')
    list_filter = ('type', 'created_at')
