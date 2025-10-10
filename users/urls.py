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
    
    # path('back-to-scratch/', views.back_to_scratch, name='back_to_scratch')
]
