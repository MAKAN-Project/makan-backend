from django.urls import path
from . import views

urlpatterns = [
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:pk>/', views.reject_request, name='reject_request'),
]
