from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_register, name="login_register"),
    path('create_user/', views.create_user, name="create_user"),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('reserve_session/', views.reserve_session, name='reserve_session'),
    path('upload_room_photo/', views.upload_room_photo, name='upload_room_photo'),
    path('create_building_project/', views.create_building_project, name='create_building_project'),
    path('customer/files/', views.customer_files, name='customer_files'),
    path('reschedule-session/<int:session_id>/', views.reschedule_session, name='reschedule_session'),
    path('choose-building-stage/', views.choose_building_stage, name='choose_building_stage'),
    path('engineering-fields/<str:stage>/', views.engineering_fields, name='engineering_fields'),
    path('engineer/<int:eng_id>/', views.engineer_details, name='engineer_details'),
    path('dashboard/ai-requests/', views.customer_ai_requests, name='customer_ai_requests'),
    path('dashboard/sessions/', views.customer_sessions, name='customer_sessions'),
    path('dashboard/3d-models/', views.customer_3d_models, name='customer_3d_models'),
    path('dashboard/profile/', views.customer_profile, name='customer_profile'),
     path('customer/projects/', views.customer_projects, name='customer_projects'),
    path('customer/project/<int:request_id>/', views.customer_project_details, name='customer_project_details'),
    # path('back-to-scratch/', views.back_to_scratch, name='back_to_scratch')
]
