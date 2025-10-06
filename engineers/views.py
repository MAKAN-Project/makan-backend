from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from projectrequests.models import ProjectRequest
from sessions_app.models import Session
from files.models import File
from users.models import User
from .forms import EngineerProfileForm
from engineers.models import Engineer

def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in.")
        return redirect('login_register')

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login_register')

    try:
        engineer = Engineer.objects.get(user=user)
    except Engineer.DoesNotExist:
        messages.warning(request, "You need to complete your profile first.")
        return redirect('engineer_complete_profile')

    if engineer.status == "pending":
        return render(request, "engineers/engineer_pending.html")
    elif engineer.status == "rejected":
        messages.warning(request, "Your profile was rejected. Please update it.")
        return redirect('engineer_complete_profile')

    # ==============================
    # Project Requests فقط للمهندس
    # ==============================
    project_requests = ProjectRequest.objects.filter(engineer=engineer).exclude(status='completed').order_by('-created_at')

    # ==============================
    # جلسات اليوم
    # ==============================
    sessions = Session.objects.filter(
        eng=engineer,
        scheduled_at__date=timezone.now().date()
    ).select_related('user')

    # ==============================
    # العدادات
    # ==============================
    pending_requests_count = project_requests.filter(status='pending').count()
    active_project_requests_count = project_requests.count()
    completed_projects_count = File.objects.filter(user=user, status='completed').count()
    pending_notifications = ProjectRequest.objects.filter(
    engineer=engineer,
    status='pending').order_by('-created_at')[:5]
    context = {
        'active_project_requests': project_requests,
        'sessions': sessions,
        'pending_requests_count': pending_requests_count,
        'active_project_requests_count': active_project_requests_count,
        'completed_projects_count': completed_projects_count,'pending_notifications': pending_notifications
    }

    return render(request, 'engineers/engineer_dashboard.html', context)


# ==========================
# إكمال ملف المهندس
# ==========================
def engineer_complete_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to complete your profile.")
        return redirect('login_register')

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login_register')

    try:
        engineer_instance = Engineer.objects.get(user=user)
    except Engineer.DoesNotExist:
        engineer_instance = None

    if request.method == "POST":
        form = EngineerProfileForm(request.POST, request.FILES, instance=engineer_instance)
        if form.is_valid():
            engineer = form.save(commit=False)
            engineer.user = user
            engineer.status = "pending"  # الأدمن سيوافق لاحقًا
            engineer.save()
            messages.success(request, "Profile submitted successfully! Waiting for admin approval.")
            return redirect("engineers_dashboard")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EngineerProfileForm(instance=engineer_instance)

    return render(request, "engineers/engineer_complete_profile.html", {"form": form})


# ==========================
# تحديث حالة طلب المشروع
# ==========================
def accept_project_request(request, request_id):
    project_request = get_object_or_404(ProjectRequest, request_id=request_id)

    if request.method == "POST":
        # استلام وقت الجلسة من الفورم
        scheduled_time = request.POST.get("scheduled_at")

        # تحقق من وجود الوقت
        if not scheduled_time:
            messages.error(request, "Please select a session date and time.")
            return redirect('engineers_dashboard')

        # تحديث حالة الطلب
        project_request.status = 'in_progress'
        project_request.save()

        # إنشاء جلسة جديدة
        Session.objects.create(
            eng=project_request.engineer,
            user=project_request.client,
            scheduled_at=scheduled_time,
            status='scheduled'
        )

        messages.success(request, f"Request #{project_request.request_id} accepted and session scheduled.")
        return redirect('engineers_dashboard')

    # إذا ما كان POST، نعرض المودال أو صفحة التأكيد
    return render(request, "engineers/schedule_session.html", {"project_request": project_request})

def reject_project_request(request, request_id):
    project_request = get_object_or_404(ProjectRequest, request_id=request_id)
    if request.method == "POST":
        project_request.status = 'rejected'
        project_request.save()
        messages.warning(request, f"Project Request #{project_request.request_id} rejected.")
    return redirect('engineers_dashboard')
