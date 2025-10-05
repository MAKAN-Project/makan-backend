from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'email', 'role', 'phone', 'address', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('role', 'created_at')
    ordering = ('user_id',)
