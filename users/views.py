# --- Reschedule Session ---
from sessions_app.models import Session
from django.shortcuts import redirect
def reschedule_session(request, session_id):
    if request.method == 'POST':
        new_time = request.POST.get('new_scheduled_at')
        session = Session.objects.get(id=session_id)
        session.scheduled_at = new_time
        session.status = 'pending_approval'  # Add this status to your model if not present
        session.save()
        # Optionally notify engineer here
        return redirect('customer_dashboard')
    return redirect('customer_dashboard')
# --- Building Project Stage Selection ---
def choose_building_stage(request):
    return render(request, 'choose_building_stage.html')

def engineering_fields(request, stage):
    from engineers.models import Engineer
    context = {'stage': stage}
    if stage == 'empty_land':
        context['architecture_engineers'] = Engineer.objects.filter(education__icontains='architecture')
        context['civil_engineers'] = Engineer.objects.filter(education__icontains='civil')
        context['interior_engineers'] = Engineer.objects.filter(education__icontains='interior')
        context['mechanical_engineers'] = Engineer.objects.filter(education__icontains='mechanical')
        return render(request, 'engineering_fields_empty_land.html', context)
    elif stage == 'empty_apartment':
        context['architecture_engineers'] = Engineer.objects.filter(education__icontains='architecture')
        context['mechanical_engineers'] = Engineer.objects.filter(education__icontains='mechanical')
        context['interior_engineers'] = Engineer.objects.filter(education__icontains='interior')
        return render(request, 'engineering_fields_empty_apartment.html', context)
    elif stage == 'with_walls':
        context['interior_engineers'] = Engineer.objects.filter(education__icontains='interior')
        context['mechanical_engineers'] = Engineer.objects.filter(education__icontains='mechanical')
        return render(request, 'engineering_fields_with_walls.html', context)
    elif stage == 'decorate':
        context['interior_engineers'] = Engineer.objects.filter(education__icontains='interior')
        return render(request, 'engineering_fields_decorate.html', context)
    elif stage == '3d_furniture':
        return render(request, 'engineering_fields_3d_furniture.html', context)
    else:
        context['architecture_engineers'] = []
        context['civil_engineers'] = []
        context['interior_engineers'] = []
        context['mechanical_engineers'] = []
        return render(request, 'engineering_fields.html', context)
    if stage == 'empty_land':
        context['architecture_engineers'] = Engineer.objects.filter(education__icontains='architecture')
        context['civil_engineers'] = Engineer.objects.filter(education__icontains='civil')
        context['interior_engineers'] = Engineer.objects.filter(education__icontains='interior')
        context['mechanical_engineers'] = Engineer.objects.filter(education__icontains='mechanical')
        return render(request, 'engineering_fields_empty_land.html', context)
    elif stage == 'empty_apartment':
        context['architecture_engineers'] = Engineer.objects.filter(education__icontains='architecture')
        context['mechanical_engineers'] = Engineer.objects.filter(education__icontains='mechanical')
        context['interior_engineers'] = Engineer.objects.filter(education__icontains='interior')
        return render(request, 'engineering_fields_empty_apartment.html', context)
    else:
        context['architecture_engineers'] = []
        context['civil_engineers'] = []
        context['interior_engineers'] = []
        context['mechanical_engineers'] = []
        return render(request, 'engineering_fields.html', context)
# --- Customer Dashboard Form Actions ---
def reserve_session(request):
    # TODO: Implement reservation logic
    return redirect('customer_dashboard')

def upload_room_photo(request):
    # TODO: Implement room photo upload logic
    return redirect('customer_dashboard')

def create_building_project(request):
    # TODO: Implement building project creation logic
    return redirect('customer_dashboard')
def home(request):
    return customer_dashboard(request)
from django.shortcuts import render,redirect
from airequests.models import AIRequest
from engineers.models import Engineer
from sessions_app.models import Session
from .models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password


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

    context = {
        'user': user,
        'engineer': Engineer.objects.all(),
        'recent_ai_requests': ai_requests[:5],
        'upcoming_sessions': upcoming_sessions,
        'total_requests': ai_requests.count(),
        'pending_requests': 0,  
        'total_sessions': Session.objects.filter(user_id=user_id).count(),
        'total_3d_models': user_3d_models.count(),
        'reserve_consulting_session_form': reserve_consulting_session_form,
        'upload_room_photo_form': upload_room_photo_form,
        'create_building_project_form': create_building_project_form,
    }
    
    return render(request, "customer_dashboard.html", context)