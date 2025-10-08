"""
URL configuration for makan_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    #path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),  
    path('', views.home, name='home'),              # لوحة الإدارة
    path('sessions/', include('sessions_app.urls')), # كل روابط جلساتك
    path('users/', include('users.urls')),          # روابط users
    path('requests/', include('airequests.urls')),  # روابط airequests
    path('category/', include('category.urls')),    # روابط category
    path('engineers/', include('engineers.urls')),  # روابط engineers
    path('files/', include('files.urls')),          # روابط files
    path('models3d/', include('models3d.urls')),    # روابط models3d
    path('payments/', include('payments.urls')),    # روابط payments

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
