from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

def home(request):
    return render(request, 'portal/index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # We use email as the username
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials or user does not exist.')
            return redirect('login')

    return render(request, 'portal/login.html')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        role = request.POST.get('role')
        studentId = request.POST.get('studentId')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        batch = request.POST.get('batch')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        
        # Create profile
        Profile.objects.create(
            user=user,
            role=role,
            student_id=studentId,
            phone=phone,
            department=department,
            batch=batch
        )

        # Log the user in
        login(request, user)
        return redirect('home')

    return render(request, 'portal/register.html')

def logout_view(request):
    logout(request)
    return redirect('home')
