from django.urls import path
from .views import NotificationListView, MarkAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications_list'),
    path('<int:pk>/read/', MarkAsReadView.as_view(), name='mark_as_read'),
]
