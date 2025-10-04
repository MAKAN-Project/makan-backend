from django.contrib import admin
from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'eng', 'scheduled_at', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'eng__user__first_name', 'eng__user__last_name', 'status')
    list_filter = ('status', 'scheduled_at')