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
            message=f"طلب جديد من {client.first_name} {client.last_name} بخصوص '{project_request.description[:30]}...'."
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
        Session.objects.create(
            user=client,
            eng=engineer,
            scheduled_at=scheduled_at,
            status="pending"
        )

        # ✅ تحديث الـ Slot
        slot.is_booked = True
        slot.save()

        messages.success(request, "✅ تم إرسال طلب الجلسة والمشروع بنجاح.")
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
    from files.models import File
    from airequests.models import AIRequest
    user_id = request.session.get('user_id')
    user_images = []
    # Get File model images uploaded by user
    file_images = File.objects.filter(user_id=user_id, type__icontains='image')
    for f in file_images:
        user_images.append({'url': f.path, 'name': f.file_name})

    # Get images from AIRequest (input and output images)
    ai_images = AIRequest.objects.filter(user_id=user_id)
    for req in ai_images:
        if req.input_image_path:
            user_images.append({'url': req.input_image_path, 'name': 'AI Input'})
        if req.output_images_paths:
            # If multiple output images, split by comma
            for out_img in req.output_images_paths.split(','):
                user_images.append({'url': out_img.strip(), 'name': 'AI Output'})

    # TODO: Populate engineer_images, engineer_pdfs, engineer_cad_files from File model (received files)
    context = {
        'user_uploaded_images': user_images,
        'engineer_images': [],
        'engineer_pdfs': [],
        'engineer_cad_files': [],
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
    # تحقق إذا المستخدم مسجل دخول
    if 'user_id' not in request.session:
        messages.error(request, "Please log in first")
        return redirect('login_register')
    
    # تحقق إذا المستخدم customer
    if request.session.get('role') != 'customer':
        messages.error(request, "Access denied")
        return redirect('home')
    
    user_id = request.session['user_id']
    
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('login_register')
    
    # جلب البيانات المطلوبة
    ai_requests = AIRequest.objects.filter(user_id=user_id).order_by('-created_at')
    
    # الجلسات القادمة
    from datetime import datetime
    upcoming_sessions = Session.objects.filter(
        user_id=user_id,
        scheduled_at__gte=datetime.now(),
        status='approved'
    ).order_by('scheduled_at')[:3]
    
    # جلب 3D models
    from models3d.models import Model3D
    user_3d_models = Model3D.objects.filter(user_id=user_id)
    

    from .forms import ReserveConsultingSessionForm, UploadRoomPhotoForm, CreateBuildingProjectForm
    # Get all approved engineers
    engineer_qs = Engineer.objects.filter(status="approved")
    # Example: Use education field as type (customize as needed)
    engineer_types = sorted(set(e.education for e in engineer_qs if e.education))
    engineer_type_choices = [(et, et) for et in engineer_types]
    engineer_choices = [(e.eng_id, f"{e.user.first_name} {e.user.last_name}") for e in engineer_qs]
    reserve_consulting_session_form = ReserveConsultingSessionForm()
    reserve_consulting_session_form.fields['engineer_type'].choices = engineer_type_choices
    reserve_consulting_session_form.fields['engineer_id'].choices = engineer_choices
    upload_room_photo_form = UploadRoomPhotoForm()
    create_building_project_form = CreateBuildingProjectForm()
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in first")
        return redirect('login_register')


    pending_notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).order_by('-created_at')

    all_notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')

    context = {
    'user': user,
    'engineers': Engineer.objects.filter(status="approved"),
    'recent_ai_requests': ai_requests[:5],
    'upcoming_sessions': upcoming_sessions,
    'total_requests': ai_requests.count(),
    'pending_requests': 0,  
    'total_sessions': Session.objects.filter(user_id=user_id).count(),
    'total_3d_models': user_3d_models.count(),
    'reserve_consulting_session_form': reserve_consulting_session_form,
    'upload_room_photo_form': upload_room_photo_form,
    'create_building_project_form': create_building_project_form,
    'pending_notifications': pending_notifications,
    'all_notifications': all_notifications,
}
    return render(request, "customer_dashboard.html", context)

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