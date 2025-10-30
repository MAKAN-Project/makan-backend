from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from projectrequests.models import ProjectRequest
from sessions_app.models import Session
from files.models import File
from users.models import User
from .forms import EngineerProfileForm
from engineers.models import Engineer
from notifications.models import Notification
from utils.zoom_api import create_zoom_meeting
from django.utils.dateparse import parse_datetime
from .models import EngineerAvailability
from django.db.models import Q
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
    notifications = Notification.objects.filter(
    recipient=user
        ).order_by('-created_at')[:10]
    context = {
        'active_project_requests': project_requests,
        'sessions': sessions,
        'pending_requests_count': pending_requests_count,
        'active_project_requests_count': active_project_requests_count,
        'completed_projects_count': completed_projects_count,
        'notifications': notifications
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




def accept_project_request(request, request_id):
    project_request = get_object_or_404(ProjectRequest, request_id=request_id)

    if request.method == "POST":
        scheduled_time_str = request.POST.get("scheduled_at")
        scheduled_time = parse_datetime(scheduled_time_str)
        if not scheduled_time:
            messages.error(request, "Please provide a valid date and time.")
            return redirect("engineers_dashboard")

        # تحديث حالة الطلب
        project_request.status = 'in_progress'
        project_request.save()

        # ✅ إنشاء اجتماع Zoom فعلي
        meeting = create_zoom_meeting(
            topic=f"Project Meeting - Request #{project_request.request_id}",
            start_time=scheduled_time,
            duration=60,
            agenda=f"Discussion for project request #{project_request.request_id}"
        )

        join_link = meeting.get("join_url") if meeting else None
        host_link = meeting.get("start_url") if meeting else None

        # ✅ إنشاء الجلسة في قاعدة البيانات
        session = Session.objects.create(
            eng=project_request.engineer,
            user=project_request.client,
            scheduled_at=scheduled_time,
            meeting_link=join_link,
            host_link=host_link,
            status='scheduled'
        )

        # ✅ ربط الطلب بالجسلة
        project_request.session = session
        project_request.save()

        # ✅ إشعار العميل بالرابط
        Notification.objects.create(
            sender=project_request.engineer.user,
            recipient=project_request.client,
            project_request=project_request,
            type='accepted',
            message=(
                f"✅ Your project request #{project_request.request_id} has been accepted!\n\n"
                f"🕒 Meeting scheduled at: {scheduled_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"🎥 Join your Zoom session here:\n<a href='{join_link}' target='_blank'>{join_link}</a>"
                if join_link else
                f"Your project request #{project_request.request_id} has been accepted, "
                f"but Zoom meeting could not be created."
            ),
            created_at=timezone.now()
        )

        # ✅ إشعار المهندس بالرابط الخاص بالمضيف
        Notification.objects.create(
            sender=project_request.engineer.user,
            recipient=project_request.engineer.user,
            project_request=project_request,
            type='zoom_host_link',
            message=(
                f"🎯 Zoom meeting created for project #{project_request.request_id}.\n\n"
                f"Host your session here:\n<a href='{host_link}' target='_blank'>{host_link}</a>"
                if host_link else
                f"Zoom meeting created, but no host link was returned."
            ),
            created_at=timezone.now()
        )

        messages.success(request, f"Request #{project_request.request_id} accepted and Zoom meeting created.")
        return redirect('engineers_dashboard')

    return redirect('engineers_dashboard')

def create_zoom_meeting_view(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.method == "POST":
        zoom_data = create_zoom_meeting(
            topic=f"Session with {session.user.first_name}",
            start_time=session.scheduled_at,
            duration=60
        )
        if zoom_data:
            session.meeting_link = zoom_data.get("join_url")
            session.host_link = zoom_data.get("start_url")
            session.status = "scheduled"
            session.save()

            messages.success(request, "✅ Zoom meeting created successfully!")
        else:
            messages.error(request, "❌ Failed to create Zoom meeting.")
    return redirect("engineers_dashboard")

def reject_project_request(request, request_id):
    project_request = get_object_or_404(ProjectRequest, request_id=request_id)

    if request.method == "POST":
        project_request.status = 'rejected'
        project_request.save()

        # 📨 إرسال إشعار للعميل
        Notification.objects.create(
            sender=project_request.engineer.user,  # المهندس الرافض
            recipient=project_request.client,      # العميل صاحب الطلب
            project_request=project_request,
            type='rejected',
            message=f"Your project request #{project_request.request_id} has been rejected by {project_request.engineer.user.first_name}.",
            created_at=timezone.now()
        )

        messages.warning(request, f"Project Request #{project_request.request_id} rejected and client notified.")

    return redirect('engineers_dashboard')


def approve_reschedule(request, session_id):
    """المهندس يوافق على إعادة الجدولة"""
    session = get_object_or_404(Session, id=session_id)
    
    # تحديث الحالة إلى approved بعد الموافقة
    session.status = 'approved'
    session.save()

    # 📨 إشعار العميل بالموافقة
    Notification.objects.create(
        sender=session.eng.user,
        recipient=session.user,
        type='reschedule_approved',
        message=f"تمت الموافقة على إعادة جدولة الجلسة إلى {session.scheduled_at.strftime('%Y-%m-%d %H:%M')}.",
    )

    messages.success(request, "✅ تمت الموافقة على إعادة الجدولة.")
    return redirect('engineers_dashboard')

def reject_reschedule(request, session_id):
    """المهندس يرفض إعادة الجدولة"""
    session = get_object_or_404(Session, id=session_id)
    
    # نعيد الجلسة للحالة السابقة
    session.status = 'scheduled'
    session.save()

    # 📨 إشعار العميل بالرفض
    Notification.objects.create(
        sender=session.eng.user,
        recipient=session.user,
        type='reschedule_rejected',
        message=f"تم رفض طلب إعادة الجدولة للجلسة المحددة بتاريخ {session.scheduled_at.strftime('%Y-%m-%d %H:%M')}.",
    )

    messages.warning(request, "❌ تم رفض طلب إعادة الجدولة.")
    return redirect('engineers_dashboard')


def manage_availability(request):
    """عرض وإضافة المواعيد المتاحة للمهندس"""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in.")
        return redirect('login_register')

    engineer = get_object_or_404(Engineer, user__user_id=user_id)

    if request.method == "POST":
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not date or not start_time or not end_time:
            messages.error(request, "⚠️ Please fill all fields.")
        else:
            # التحقق من عدم تداخل المواعيد
            exists = EngineerAvailability.objects.filter(
                engineer=engineer,
                date=date,
                start_time=start_time,
                end_time=end_time
            ).exists()

            if exists:
                messages.warning(request, "This time slot already exists.")
            else:
                EngineerAvailability.objects.create(
                    engineer=engineer,
                    date=date,
                    start_time=start_time,
                    end_time=end_time
                )
                messages.success(request, "✅ Availability added successfully!")

    availabilities = EngineerAvailability.objects.filter(engineer=engineer).order_by('date', 'start_time')

    return render(request, "engineers/manage_availability.html", {
        "availabilities": availabilities
    })


def upload_project_file(request, request_id):
    # ✅ تحقق من وجود جلسة مستخدم
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must be logged in.")
        return redirect("login_register")

    # ✅ جلب المستخدم
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("login_register")

    # ✅ جلب المهندس المرتبط بهذا المستخدم
    try:
        engineer = Engineer.objects.get(user=user)
    except Engineer.DoesNotExist:
        messages.error(request, "Engineer profile not found.")
        return redirect("engineer_complete_profile")

    # ✅ جلب المشروع المطلوب
    project = get_object_or_404(ProjectRequest, request_id=request_id)

    # ✅ تحقق إن هذا المهندس هو صاحب المشروع فعلاً
    if project.engineer != engineer:
        messages.error(request, "You are not authorized to upload files for this project.")
        return redirect("engineers_dashboard")

    # ✅ معالجة رفع الملف
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_name = request.POST.get("file_name", uploaded_file.name)
        ext = uploaded_file.name.split(".")[-1].lower()

        # 🔹 إنشاء سجل الملف في قاعدة البيانات
        file_obj = File.objects.create(
            user=project.client,  # المستلم هو العميل
            project_request=project,
            file_name=file_name,
            type=ext,
            file=uploaded_file,
            path=f"uploads/{uploaded_file.name}",
            status="pending",
        )

        # 🔹 تحديث حالة المشروع
        project.status = "in_progress"
        project.updated_at = timezone.now()
        project.save()

        # 🔹 تحديد ما إذا كان الملف ثلاثي الأبعاد
        is_3d = ext in ["obj", "fbx", "glb", "gltf", "stl"]

        # 🔹 إنشاء إشعار للعميل
        message_text = (
            f"📁 Engineer <strong>{engineer.user.first_name}</strong> "
            f"has uploaded {'a 3D file' if is_3d else 'a new file'} "
            f"for your project: <strong>{file_name}</strong>."
        )

        Notification.objects.create(
            sender=user,
            recipient=project.client,
            project_request=project,
            type="file_uploaded",
            message=message_text,
            created_at=timezone.now(),
        )

        # 🔹 رسالة نجاح
        messages.success(request, f"✅ File '{file_name}' uploaded successfully and client notified.")
        return redirect("engineers_dashboard")

    # ⚠️ لو ما في ملف
    messages.error(request, "No file selected.")
    return redirect("engineers_dashboard")

def view_requests(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(user_id=user_id)
    engineer = Engineer.objects.get(user=user)
    project_requests = ProjectRequest.objects.filter(engineer=engineer).exclude(status='completed').order_by('-created_at')
    sessions = Session.objects.filter(eng=engineer,scheduled_at__date=timezone.now().date()).select_related('user')
    pending_requests_count = project_requests.filter(status='pending').count()
    active_project_requests_count = project_requests.count()
    completed_projects_count = File.objects.filter(user=user, status='completed').count()
    notifications = Notification.objects.filter(
    recipient=user
        ).order_by('-created_at')[:10]
    context = {
        'active_project_requests': project_requests,
        'sessions': sessions,
        'pending_requests_count': pending_requests_count,
        'active_project_requests_count': active_project_requests_count,
        'completed_projects_count': completed_projects_count,
        'notifications': notifications
    }
    return render(request, "engineers/requests.html", context)

def view_sessions(request):
    q = request.GET.get("q", "").strip()  # search query
    status_filter = request.GET.get("status")  # filter by status

    # Start with all sessions
    sessions_qs = Session.objects.select_related("eng__user", "user").order_by('-scheduled_at')

    # Filter sessions for the current engineer
    engineer_id = request.session.get('user_id')
    if engineer_id and request.session.get('role') == 'engineer':
        sessions_qs = sessions_qs.filter(eng__user__user_id=engineer_id)

    # Search by client name
    if q:
        sessions_qs = sessions_qs.filter(
        Q(user__first_name__icontains=q) |
        Q(user__last_name__icontains=q)
    )

    # Filter by status if provided
    if status_filter:
        sessions_qs = sessions_qs.filter(status=status_filter)

    context = {
        "sessions": sessions_qs,
        "status_choices": Session.STATUS_CHOICES,
    }
    return render(request, "engineers/sessions_eng.html", context)