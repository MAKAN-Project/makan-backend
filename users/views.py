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
