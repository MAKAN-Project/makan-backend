from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_register, name="login_register"),
    path('create_user/', views.create_user, name="create_user"),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
]
