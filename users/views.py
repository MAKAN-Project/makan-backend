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
        scheduled_at__gte=datetime.now()
    ).order_by('scheduled_at')[:3]
    
    # جلب 3D models
    from models3d.models import Model3D
    user_3d_models = Model3D.objects.filter(user_id=user_id)
    
    context = {
        'user': user,
        'recent_ai_requests': ai_requests[:5],
        'upcoming_sessions': upcoming_sessions,
        'total_requests': ai_requests.count(),
        'pending_requests': 0,  
        'total_sessions': Session.objects.filter(user_id=user_id).count(),
        'total_3d_models': user_3d_models.count(),
    }
    
    return render(request, "customer_dashboard.html", context)