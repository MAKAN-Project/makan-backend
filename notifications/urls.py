from django.urls import path
from .views import NotificationListView, MarkAsReadView
from . import views
urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications_list'),
    path('<int:pk>/read/', MarkAsReadView.as_view(), name='mark_as_read'),
    path('unread_count/', views.unread_count, name='unread_count'),  # ✅ هذا الجديد
    path('all/', views.notifications_page, name='notifications_page'),
]
