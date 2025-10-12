from django.shortcuts import render
from django.conf import settings
import os
from projectrequests.models import ProjectRequest
from engineers.models import Engineer
from users.models import User
from notifications.models import Notification
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from sessions_app.models import Session
from notifications.models import Notification
from users.models import User
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import make_aware



def home(request):
    selected_filter = request.GET.get('filter', 'All').lower()
    items = []
    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    folder_map = {'architecture': 'arch', 'interior': 'dicor', '3d_models': '3d'}

    # 🔹 Portfolio logic (بدون تغيير)
    folder = folder_map.get(selected_filter)
    if folder:
        folder_dir = os.path.join(settings.MEDIA_ROOT, 'projects', folder)
        files = sorted(os.listdir(folder_dir), reverse=True) if os.path.exists(folder_dir) else []
        for fname in files[:4]:
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                items.append({
                    'url': f"{media_url}projects/{folder}/{fname}",
                    'file_type': 'image',
                    'file_name': fname,
                    'category': selected_filter
                })
    else:
        for cat, folder_name in folder_map.items():
            folder_dir = os.path.join(settings.MEDIA_ROOT, 'projects', folder_name)
            files = sorted(os.listdir(folder_dir), reverse=True) if os.path.exists(folder_dir) else []
            for fname in files[:4]:
                if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    items.append({
                        'url': f"{media_url}projects/{folder_name}/{fname}",
                        'file_type': 'image',
                        'file_name': fname,
                        'category': cat
                    })

    # 🔹 Engineers
    engineers = Engineer.objects.filter(status="approved")

    # 🔹 Notifications (المشكلة كانت هنا)
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(user_id=request.session["user_id"])
        except User.DoesNotExist:
            user = None

    if user:
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')[:5]

        all_notifications = Notification.objects.filter(
            recipient=user
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')
    else:
        pending_notifications = []
        all_notifications = []

    return render(request, 'home.html', {
        'portfolio_items': items,
        'selected_filter': selected_filter,
        'service_images': [
            '/static/images/1.webp',
            '/static/images/2.webp',
            '/static/images/3.webp',
            '/static/images/4.webp'
        ],
        'engineers': engineers,
        'pending_notifications': pending_notifications,
        'all_notifications': all_notifications,
    })


def projects(request):
    """Display all projects with filtering by engineering specialization"""
    specialization_filter = request.GET.get('specialization', '')
    
    # Get notifications for logged-in users
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(user_id=request.session["user_id"])
        except User.DoesNotExist:
            user = None

    if user:
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')[:5]
    else:
        pending_notifications = []
    
    # Filter projects based on specialization - show only completed projects
    if specialization_filter:
        projects = ProjectRequest.objects.filter(
            engineer__specialization=specialization_filter,
            status='completed'
        ).select_related('engineer', 'engineer__user', 'client').order_by('-created_at')
    else:
        projects = ProjectRequest.objects.filter(
            status='completed'
        ).select_related('engineer', 'engineer__user', 'client').order_by('-created_at')
    
    # Get display name for current filter
    specialization_choices = dict(Engineer.SPECIALIZATION_CHOICES)
    current_filter_display = specialization_choices.get(specialization_filter, 'All Projects')
    
    context = {
        'projects': projects,
        'current_filter': specialization_filter,
        'current_filter_display': current_filter_display,
        'pending_notifications': pending_notifications,
    }
    
    return render(request, 'projects.html', context)


def engineers_list(request):
    """Display all approved engineers with filtering by specialization"""
    specialization_filter = request.GET.get('specialization', '')
    
    # Get notifications for logged-in users
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(user_id=request.session["user_id"])
        except User.DoesNotExist:
            user = None

    if user:
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')[:5]
    else:
        pending_notifications = []
    
    # Filter engineers based on specialization - show only approved engineers
    if specialization_filter:
        engineers = Engineer.objects.filter(
            specialization=specialization_filter,
            status='approved'
        ).select_related('user').order_by('-created_at')
    else:
        engineers = Engineer.objects.filter(
            status='approved'
        ).select_related('user').order_by('-created_at')
    
    # Get display name for current filter
    specialization_choices = dict(Engineer.SPECIALIZATION_CHOICES)
    current_filter_display = specialization_choices.get(specialization_filter, 'All Engineers')
    
    context = {
        'engineers': engineers,
        'current_filter': specialization_filter,
        'current_filter_display': current_filter_display,
        'pending_notifications': pending_notifications,
    }
    
    return render(request, 'engineers_list.html', context)


def services(request):
    """Display comprehensive services page"""
    # Get notifications for logged-in users
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(user_id=request.session["user_id"])
        except User.DoesNotExist:
            user = None

    if user:
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')[:5]
    else:
        pending_notifications = []
    
    context = {
        'pending_notifications': pending_notifications,
    }
    
    return render(request, 'services.html', context)


def about(request):
    """Display comprehensive about page with vision and future features"""
    # Get notifications for logged-in users
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(user_id=request.session["user_id"])
        except User.DoesNotExist:
            user = None

    if user:
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')[:5]
    else:
        pending_notifications = []
    
    context = {
        'pending_notifications': pending_notifications,
    }
    
    return render(request, 'about.html', context)


def contact(request):
    """Display contact page with team member information"""
    # Get notifications for logged-in users
    user = None
    if request.session.get("user_id"):
        try:
            user = User.objects.get(user_id=request.session["user_id"])
        except User.DoesNotExist:
            user = None

    if user:
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).select_related('sender', 'project_request', 'session').order_by('-created_at')[:5]
    else:
        pending_notifications = []
    
    # Team members information
    team_members = [
        {
            'name': 'Mahmoud Shuman',
            'role': 'CEO & Co-Founder',
            'email': 'mahmoud.shuman@outlook.com',
            'description': 'Visionary leader with extensive experience in architecture and technology innovation'
        },
        {
            'name': 'Omyma Alkurd',
            'role': 'CTO & Co-Founder',
            'email': 'omyma_1994@hotmail.com',
            'description': 'Technology expert specializing in AI-driven design solutions and platform development'
        },
        {
            'name': 'Dalia Saymeh',
            'role': 'Head of Engineering',
            'email': 'dalia.saymeh@makan.com',
            'description': 'Senior engineer with expertise in structural design and sustainable architecture'
        },
        {
            'name': 'Hamza Sammour',
            'role': 'Head of Operations',
            'email': 'hamza.sammour@makan.com',
            'description': 'Operations specialist focused on platform optimization and client success'
        }
    ]
    
    context = {
        'pending_notifications': pending_notifications,
        'team_members': team_members,
    }
    
    return render(request, 'contact.html', context)



