from django.shortcuts import render, redirect
from django.contrib import messages
from airequests.models import AIRequest
from engineers.models import Engineer
from sessions_app.models import Session
from files.models import File
from users.models import User
from .forms import EngineerProfileForm

# ==========================
# Dashboard للمهندس
# ==========================
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

    # تحقق إذا المهندس أكمل ملفه
    try:
        engineer = Engineer.objects.get(user=user)
    except Engineer.DoesNotExist:
        messages.warning(request, "You need to complete your profile first.")
        return redirect('engineer_complete_profile')

    # تحقق من حالة المهندس
    if engineer.status == "pending":
        # لو الحساب بيندنج، اعرض صفحة انتظار
        return render(request, "engineers/engineer_pending.html")
    elif engineer.status == "rejected":
        messages.warning(request, "Your profile was rejected. Please update it.")
        return redirect('engineer_complete_profile')

    # Active Requests
    requests = AIRequest.objects.filter(user=user)

    # Sessions للمهندس
    sessions = Session.objects.filter(eng=engineer)

    # العدادات
    pending_requests_count = requests.count()
    upcoming_sessions_count = sessions.count()
    completed_projects_count = File.objects.filter(user=user).count()

    context = {
        'requests': requests,
        'sessions': sessions,
        'pending_requests_count': pending_requests_count,
        'upcoming_sessions_count': upcoming_sessions_count,
        'completed_projects_count': completed_projects_count,
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

    # تحقق إذا لديه ملف موجود مسبقًا
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
