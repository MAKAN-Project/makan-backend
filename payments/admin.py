from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'amount', 'status', 'method', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'status', 'method')
    list_filter = ('status', 'method', 'created_at')

