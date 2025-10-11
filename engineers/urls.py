from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='engineers_dashboard'),
    path('complete-profile/', views.engineer_complete_profile, name='engineer_complete_profile'),

    # تحديث حالة طلب AI
   # path('ai-request/<int:request_id>/accept/', views.accept_ai_request, name='accept_ai_request'),
    #path('ai-request/<int:request_id>/reject/', views.reject_ai_request, name='reject_ai_request'),

    # تحديث حالة طلب مشروع

    # path('project_request/<int:request_id>/accept/', views.accept_project_request, name='accept_project_request'),
    path('accept_project_request/<int:request_id>/', views.accept_project_request, name='accept_project_request'),

    path('project_request/<int:request_id>/reject/', views.reject_project_request, name='reject_project_request'),
    path('approve_reschedule/<int:session_id>/', views.approve_reschedule, name='approve_reschedule'),
    path('reject_reschedule/<int:session_id>/', views.reject_reschedule, name='reject_reschedule'),
    path('create-zoom-meeting/<int:session_id>/', views.create_zoom_meeting_view, name='create_zoom_meeting'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('upload-file/<int:request_id>/', views.upload_project_file, name='upload_project_file'),

]
