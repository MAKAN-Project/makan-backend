from django.contrib import admin
from .models import Engineer


@admin.register(Engineer)
class EngineerAdmin(admin.ModelAdmin):
    list_display = ('eng_id', 'user', 'education', 'status', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'education')
    list_filter = ('status', 'created_at')
