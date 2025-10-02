from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='engineers_dashboard'),   # الصفحة الرئيسية للمهندسين
    #path('projects/', views.projects, name='engineers_projects'),  # صفحة المشاريع
    #path('profile/<int:id>/', views.profile, name='engineers_profile'), # صفحة البروفايل
]