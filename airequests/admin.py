from django.contrib import admin
from .models import AIRequest

@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('ai_request_id', 'user', 'style', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'style')
    list_filter = ('style', 'created_at')

