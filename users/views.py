# --- Reschedule Session ---
from notifications.models import Notification
from sessions_app.models import Session
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from projectrequests.models import ProjectRequest
from sessions_app.models import Session
from files.models import File
from users.models import User
from engineers.models import Engineer
from django.contrib.auth.hashers import make_password, check_password
from airequests.models import AIRequest
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings
from notifications.utils import create_notification
from engineers.models import EngineerAvailability
from django.db.models import Q
from models3d.models import Model3D
from datetime import date
def reschedule_session(request, session_id):
    if request.method == 'POST':
        new_date = request.POST.get('date')
        new_time = request.POST.get('time')

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            messages.error(request, "⚠️ الجلسة غير موجودة.")
            return redirect('sessions_list')

        # دمج التاريخ والوقت الجديد
        try:
            new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            messages.error(request, "⚠️ التاريخ أو الوقت غير صالح.")
            return redirect('sessions_list')

        # ✅ حفظ الوقت القديم قبل التعديل
        session.old_scheduled_at = session.scheduled_at
        session.scheduled_at = new_datetime
        session.status = 'reschedule_pending'
        session.save()

        # ✅ إنشاء إشعار للمهندس
        Notification.objects.create(
            recipient=session.eng.user,  # المهندس
            sender=User.objects.get(user_id=request.session['user_id']),  # العميل الحالي
            type='reschedule',
            message=f"قام {request.session.get('first_name')} بطلب إعادة جدولة الجلسة من {session.old_scheduled_at.strftime('%Y-%m-%d %H:%M')} إلى {new_datetime.strftime('%Y-%m-%d %H:%M')}.",
        )

        messages.success(request, "✅ تم إرسال طلب إعادة الجدولة بنجاح.")
        return redirect('sessions_list')

    return redirect('sessions_list')



# --- Building Project Stage Selection ---
def choose_building_stage(request):
    return render(request, 'choose_building_stage.html')

def engineering_fields(request, stage):
    context = {'stage': stage}
    if stage == 'empty_land':
        context['architecture_engineers'] = Engineer.objects.filter(specialization='architecture')
        context['civil_engineers'] = Engineer.objects.filter(specialization='civil')
        context['interior_engineers'] = Engineer.objects.filter(specialization='interior')
        context['mechanical_engineers'] = Engineer.objects.filter(specialization='mechanical')
        return render(request, 'engineering_fields_empty_land.html', context)
    elif stage == 'empty_apartment':
        context['architecture_engineers'] = Engineer.objects.filter(specialization='architecture')
        context['mechanical_engineers'] = Engineer.objects.filter(specialization='mechanical')
        context['interior_engineers'] = Engineer.objects.filter(specialization='interior')
        return render(request, 'engineering_fields_empty_apartment.html', context)
    elif stage == 'decorate':
        context['mechanical_engineers'] = Engineer.objects.filter(specialization='mechanical')
        context['interior_engineers'] = Engineer.objects.filter(specialization='interior')
        return render(request, 'engineering_fields_decorate.html', context)
    elif stage == '3d_furniture':
        context['interior_engineers'] = Engineer.objects.filter(specialization='interior')
        return render(request, 'engineering_fields_3d_furniture.html', context)
    else:
        context['architecture_engineers'] = []
        context['civil_engineers'] = []
        context['interior_engineers'] = []
        context['mechanical_engineers'] = []
        return render(request, 'engineering_fields.html', context)
    
# --- Customer Dashboard Form Actions ---
def reserve_session(request):
    print(list(messages.get_messages(request)))

    engineer_id = request.GET.get('engineer_id') or request.POST.get('engineer_id')

    available_slots = []
    if engineer_id:
        available_slots = EngineerAvailability.objects.filter(
            engineer_id=engineer_id,
            is_booked=False,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')

    if request.method == 'POST':
        project_description = request.POST.get('project_description')
        customer_files = request.FILES.getlist('file')
        selected_slot_id = request.POST.get('selected_slot')
        user_id = request.session.get('user_id')

        # ✅ تحقق من البيانات المطلوبة
        if not user_id or not engineer_id or not selected_slot_id:
            messages.error(request, "⚠️ Missing required information.")
            return render(request, 'engineer_details.html', {'available_slots': available_slots})

        try:
            client = User.objects.get(user_id=user_id)
            engineer = Engineer.objects.get(eng_id=engineer_id)
            slot = EngineerAvailability.objects.get(id=selected_slot_id, engineer=engineer, is_booked=False)
        except User.DoesNotExist:
            messages.error(request, "⚠️ User not found.")
            return redirect('login_register')
        except Engineer.DoesNotExist:
            messages.error(request, "⚠️ Engineer not found.")
            return redirect('home')
        except EngineerAvailability.DoesNotExist:
            messages.error(request, "⚠️ Selected slot is no longer available.")
            return redirect('engineer_details', eng_id=engineer_id)

        # ✅ دمج التاريخ والوقت
        scheduled_at = timezone.make_aware(datetime.combine(slot.date, slot.start_time))

        # ✅ إنشاء المشروع
        project_request = ProjectRequest.objects.create(
            client=client,
            engineer=engineer,
            description=project_description or "No description provided",
            status='pending',
            selected_availability=slot
        )

        # ✅ إنشاء إشعار للمهندس
        Notification.objects.create(
            recipient=engineer.user,        # المهندس المستقبِل
            sender=client,                  # العميل المرسل
            project_request=project_request,
            type='project_request',         # مطابق للـ choices
            message=f"New Request {client.first_name} {client.last_name} About '{project_request.description[:30]}...'."
        )

        # ✅ حفظ الملفات
        if customer_files:
            for f in customer_files:
                if not f:
                    continue
                File.objects.create(
                    type=f.content_type.split('/')[-1],
                    file_name=f.name,
                    file=f,
                    user=client,
                    project_request=project_request
                )

        # ✅ إنشاء الجلسة (Session)
        session=Session.objects.create(
            user=client,
            eng=engineer,
            scheduled_at=scheduled_at,
            status="pending"
        )

        project_request.session = session
        project_request.save()
        # ✅ تحديث الـ Slot
        slot.is_booked = True
        slot.save()

        messages.success(request, "✅ Send project Request Succesfuly.")
        return redirect('engineer_details', eng_id=engineer_id)

    return render(request, 'engineer_details.html', {
        'available_slots': available_slots,
    })

def upload_room_photo(request):
    # TODO: Implement room photo upload logic
    return redirect('customer_dashboard')

def create_building_project(request):
    # TODO: Implement building project creation logic
    return redirect('customer_dashboard')

def home(request):
    return customer_dashboard(request)


def login_register(request):
    return render(request, "login_register.html")

def logout_user(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('home')

# --- Customer Files Page ---
def customer_files(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('login_register')

    # Fetch user files
    files = File.objects.filter(user_id=user_id).order_by('-created_at')

    # Split by type for clarity
    image_extensions = ['jpg', 'jpeg', 'png', 'gif']
    pdf_extensions = ['pdf']
    cad_extensions = ['dwg', 'dxf']

    image_files = []
    pdf_files = []
    cad_files = []
    other_files = []

    for f in files:
        ext = f.file_name.split('.')[-1].lower()
        file_data = {'url': f.file.name, 'name': f.file_name, 'type': f.type, 'status': f.status}
        if ext in image_extensions:
            image_files.append(file_data)
        elif ext in pdf_extensions:
            pdf_files.append(file_data)
        elif ext in cad_extensions:
            cad_files.append(file_data)
        else:
            other_files.append(file_data)

    context = {
        'image_files': image_files,
        'pdf_files': pdf_files,
        'cad_files': cad_files,
        'other_files': other_files,
    }
    return render(request, 'customer_files.html', context)

# ===== User Management =====
def create_user(request):
    if request.method == 'POST':
        errors = User.objects.user_validator(request.POST)
        if errors:
            for value in errors.values():
                messages.error(request, value, extra_tags='register')
            return redirect('login_register')

        password = make_password(request.POST.get('password'))
        role = request.POST.get('role', 'customer')  # من الراديو

        user = User.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            password=password,
            phone=request.POST['phone'],
            address=request.POST['address'],
            role=role
        )

        # حفظ بيانات في session
        request.session['first_name'] = user.first_name
        request.session['user_id'] = user.user_id
        request.session['role'] = user.role

        if role == 'engineer':
            return redirect('engineer_complete_profile')  
        else:
            return redirect('customer_dashboard')

    return redirect('login_register')



def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        users = User.objects.filter(email=email)
        if users.exists():
            user = users.first()
            if check_password(password, user.password):
                request.session['first_name'] = user.first_name
                request.session['user_id'] = user.user_id
                request.session['role'] = user.role

                messages.success(request, "Logged in successfully", extra_tags='login')
                
                if user.role == 'engineer':
                    return redirect('engineers_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                messages.error(request, "Incorrect password", extra_tags='login')
        else:
            messages.error(request, "Email not found", extra_tags='login')
    return redirect('login_register')

def customer_dashboard(request):
    # --- تحقق من المستخدم ---
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first.")
        return redirect('login_register')

    if request.session.get('role') != 'customer':
        messages.error(request, "Access denied.")
        return redirect('home')

    user_id = request.session['user_id']
    user = User.objects.get(user_id=user_id)

    # --- بيانات الإشعارات ---
    notifications = Notification.objects.filter(
        recipient=user
    ).order_by('-created_at')[:5]

    
    # --- جلسات اليوم ---
    today_sessions = Session.objects.filter(
        user_id=user_id,
        scheduled_at__date=date.today()
    ).order_by('scheduled_at')

    # --- المشاريع ---
    project_requests = ProjectRequest.objects.filter(
        client=user
    ).order_by('-created_at')[:5]

    # --- الطلبات من الذكاء الصناعي ---
    ai_requests = AIRequest.objects.filter(
        user_id=user_id
    ).order_by('-created_at')[:5]

    # --- نماذج 3D ---
    user_3d_models = Model3D.objects.filter(user_id=user_id)

    # --- الإحصائيات ---
    stats = {
        'total_requests': ProjectRequest.objects.filter(client=user).count(),
        'completed_projects': ProjectRequest.objects.filter(client=user, status='completed').count(),
        'total_sessions': Session.objects.filter(user_id=user_id).count(),
        'pending_sessions': Session.objects.filter(user_id=user_id, status='pending').count(),
        'notifications_count': notifications.count(),
    }

    # --- تمرير البيانات إلى القالب ---
    context = {
        'user': user,
        'notifications': notifications,
        'today_sessions': today_sessions,
        'project_requests': project_requests,
        'ai_requests': ai_requests,
        'user_3d_models': user_3d_models,
        'stats': stats,
    }

    return render(request, 'customer_dashboard.html', context)
def engineer_details(request, eng_id):
    engineer = get_object_or_404(Engineer, pk=eng_id)
    
    # 🔹 جلب المشاريع المكتملة فقط
    projects = ProjectRequest.objects.filter(engineer=engineer).order_by('-created_at')
    projects_data = []

    for project in projects:
        if project.status.lower() != 'completed':
            continue

        project_files = File.objects.filter(project_request=project)
        thumbnail_url = ''
        thumbnail_type = 'file'

        if project_files.exists():
            first_file = project_files.first()
            file_type = first_file.type.lower()

            if file_type in ['image', 'jpg', 'jpeg', 'png']:
                thumbnail_url = first_file.file.url
                thumbnail_type = 'image'
            elif file_type in ['gltf', 'glb']:
                thumbnail_url = first_file.file.url
                thumbnail_type = 'model'
            if first_file and first_file.file:
             thumbnail_url = first_file.file.url
            else:
             thumbnail_url = '/static/images/default-thumbnail.jpg'  # أو أي صورة بديلة عندك

        projects_data.append({
            'request_id': project.request_id,
            'description': project.description,
            'status': project.status,
            'created_at': project.created_at,
            'thumbnail_url': thumbnail_url,
            'thumbnail_type': thumbnail_type,
        })

    # 🔹 جلب المواعيد المتاحة فقط (المستقبلية وغير المحجوزة)
        available_slots = EngineerAvailability.objects.filter(
            engineer=engineer,
            is_booked=False,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')


    # 🔹 تمرير البيانات للقالب
    context = {
        'engineer': engineer,
        'projects': projects_data,
        'available_slots': available_slots,  # ✅ تمام
    }

    return render(request, 'engineer_details.html', context)


def customer_ai_requests(request):
    ai_requests = AIRequest.objects.filter(user_id=request.session.get('user_id')).order_by('-created_at')
    return render(request, 'ai_requests.html', {'ai_requests': ai_requests})


def customer_sessions(request):
    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status")

    # جلب كل الجلسات من قاعدة البيانات
    sessions_qs = Session.objects.select_related("eng__user", "user").order_by('-scheduled_at')

    # إذا المستخدم الحالي هو "customer" (عميل)
    user_id = request.session.get('user_id')
    if user_id and request.session.get('role') == 'customer':
        # نعرض فقط الجلسات الخاصة فيه
        sessions_qs = sessions_qs.filter(user__user_id=user_id)

    # البحث بالاسم (اسم المهندس أو العميل)
    if q:
        sessions_qs = sessions_qs.filter(
            Q(eng__user__first_name__icontains=q) |
            Q(eng__user__last_name__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )

    # الفلترة حسب الحالة (status)
    if status_filter:
        sessions_qs = sessions_qs.filter(status=status_filter)

    # تمرير البيانات للقالب
    context = {
        "sessions": sessions_qs,
        "status_choices": Session.STATUS_CHOICES,
    }
    return render(request, "sessions.html", context)


# views.py
def customer_3d_models(request):
    # 🧩 تحقق من السيشن
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_register')  # غيّر الاسم حسب اسم صفحة تسجيل الدخول عندك

    # 📦 احضر المستخدم
    user = User.objects.get(user_id=user_id)

    # 🪑 احضر النماذج ثلاثية الأبعاد الخاصة به أو المتاحة للجميع
    furniture = Model3D.objects.filter(model_file__isnull=False).exclude(model_file='')

    # 🎨 أرسلها للصفحة
    return render(request, '3d_models.html', {'furniture': furniture, 'user': user})


def customer_profile(request):
    user = User.objects.get(user_id=request.session.get('user_id'))
    return render(request, 'customer_profile.html', {'user': user})
def customer_projects(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_register')

    user = User.objects.get(user_id=user_id)
    projects = ProjectRequest.objects.filter(client=user).order_by('-created_at')
    
    context = {'projects': projects}
    return render(request, 'customer_projects.html', context)


def customer_project_details(request, request_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_register')

    user = User.objects.get(user_id=user_id)

    try:
        project = ProjectRequest.objects.get(request_id=request_id, client=user)
        files = File.objects.filter(project_request=project)
    except ProjectRequest.DoesNotExist:
        return render(request, '404.html', {'message': 'Project not found.'})

    context = {
        'project': project,
        'files': files
    }
    return render(request, 'customer_project_detail.html', context)
