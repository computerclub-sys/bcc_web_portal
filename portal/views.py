from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Profile, MembershipApplication

def home(request):
    return render(request, 'portal/index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
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
        
        Profile.objects.create(
            user=user,
            student_id=studentId,
            phone=phone,
            department=department,
            batch=batch
        )

        login(request, user)
        return redirect('home')

    return render(request, 'portal/register.html')

@login_required
def profile_view(request):
    profile = request.user.profile
    application = MembershipApplication.objects.filter(user=request.user).first()
    return render(request, 'portal/profile.html', {
        'profile': profile,
        'application': application,
    })

@login_required
def apply_membership(request):
    if request.method == 'POST':
        if hasattr(request.user, 'membership_application'):
            messages.error(request, 'You have already applied for membership.')
            return redirect('profile')
        
        MembershipApplication.objects.create(user=request.user)
        messages.success(request, 'Membership application submitted successfully! Wait for admin approval.')
        return redirect('profile')
    
    return redirect('profile')

def member_public_view(request, member_uuid):
    profile = get_object_or_404(Profile, member_uuid=member_uuid, is_member=True)
    return render(request, 'portal/member_card.html', {'profile': profile})

def logout_view(request):
    logout(request)
    return redirect('home')
