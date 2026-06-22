from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from .models import Profile
from events.models import Event
from cse_fest.models import Fest

def home(request):
    from .models import TeamMember

    active_events = Event.objects.filter(status='active').order_by('date')[:3]
    completed_events = Event.objects.filter(status='completed').order_by('-date')[:3]
    cse_fests = Fest.objects.filter(is_active=True).order_by('-year')

    president = TeamMember.objects.filter(leader_position='president', is_active=True).first()
    gs = TeamMember.objects.filter(leader_position='general_secretary', is_active=True).first()
    vps = list(TeamMember.objects.filter(leader_position='vice_president', is_active=True).order_by('leader_order'))
    vps_row1 = vps[:4]
    vps_row2 = vps[4:]
    while len(vps_row1) < 4:
        vps_row1.append(None)

    return render(request, 'portal/index.html', {
        'active_events': active_events,
        'completed_events': completed_events,
        'cse_fests': cse_fests,
        'president': president,
        'gs': gs,
        'vps_row1': vps_row1,
        'vps_row2': vps_row2,
    })

def team(request):
    from .models import TeamMember

    panels_data = [
        {'key': 'advisory', 'title': 'Advisory Panel', 'subtitle': 'Guiding the club with wisdom and experience', 'members': TeamMember.objects.filter(panel='advisory', is_active=True)},
        {'key': 'leading', 'title': 'Leading Panel', 'subtitle': 'Leading the club with vision and dedication', 'members': TeamMember.objects.filter(panel='leading', is_active=True)},
        {'key': 'tech', 'title': 'Tech Panel', 'subtitle': 'Building and innovating with technology', 'members': TeamMember.objects.filter(panel='tech', is_active=True)},
        {'key': 'social_media', 'title': 'Social Media & Relations Panel', 'subtitle': 'Connecting with the community and spreading the word', 'members': TeamMember.objects.filter(panel='social_media', is_active=True)},
        {'key': 'treasurer', 'title': 'Treasurer Panel', 'subtitle': 'Managing club finances and budgeting', 'members': TeamMember.objects.filter(panel='treasurer', is_active=True)},
        {'key': 'organizing', 'title': 'Organizing Panel', 'subtitle': 'Coordinating events and club activities', 'members': TeamMember.objects.filter(panel='organizing', is_active=True)},
        {'key': 'executive', 'title': 'Executive Members', 'subtitle': 'Making events happen seamlessly', 'members': TeamMember.objects.filter(panel='executive', is_active=True)},
    ]
    return render(request, 'portal/team.html', {'panels_data': panels_data})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials or user does not exist.')
            return redirect('login')

    return render(request, 'portal/login.html')

def register_view(request):
    member_uuid = request.GET.get('member_uuid') or request.POST.get('member_uuid')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        if not member_uuid:
            messages.error(request, 'Invalid registration link. Please scan your membership card.')
            return redirect('register')

        try:
            profile = Profile.objects.get(member_uuid=member_uuid, user__isnull=True, is_member=True)
        except Profile.DoesNotExist:
            messages.error(request, 'This membership card is already linked to an account or is invalid.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect(f'/register/?member_uuid={member_uuid}')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect(f'/register/?member_uuid={member_uuid}')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        profile.user = user
        profile.email = email
        profile.is_member = True
        profile.claim()
        profile.save()

        login(request, user)
        return redirect('member_claim', member_uuid=member_uuid)

    return render(request, 'portal/register.html', {'member_uuid': member_uuid})

@login_required
def profile_view(request):
    if request.user.is_superuser:
        return render(request, 'portal/error_no_profile.html', {'is_superuser': True}, status=404)
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return render(request, 'portal/error_no_profile.html', {'is_superuser': False}, status=404)
    return render(request, 'portal/profile.html', {
        'profile': profile,
    })

@login_required
def profile_update_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return render(request, 'portal/error_no_profile.html', {'is_superuser': False}, status=404)

    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.department = request.POST.get('department', '')
        profile.batch = request.POST.get('batch', '')
        new_email = request.POST.get('email', request.user.email)
        request.user.email = new_email
        request.user.username = new_email
        request.user.first_name = request.POST.get('name', request.user.first_name)
        request.user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'portal/profile_edit.html', {'profile': profile})

def member_public_view(request, member_uuid):
    profile = get_object_or_404(Profile, member_uuid=member_uuid, is_member=True)

    if profile.is_expired:
        return render(request, 'portal/member_expired.html', {'profile': profile})

    if profile.user is not None:
        return render(request, 'portal/member_card.html', {'profile': profile})

    if not request.user.is_authenticated:
        return redirect(f'/register/?member_uuid={member_uuid}')

    return redirect('member_claim', member_uuid=member_uuid)

@login_required
def member_claim_view(request, member_uuid):
    try:
        profile = Profile.objects.get(member_uuid=member_uuid, user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'This membership card is not linked to your account.')
        return redirect('profile')

    if profile.is_expired:
        messages.error(request, 'Your membership has expired.')
        return redirect('member_public', member_uuid=member_uuid)

    if request.method == 'POST':
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        batch = request.POST.get('batch')

        profile.phone = phone
        profile.department = department
        profile.batch = batch
        if not profile.claimed_at:
            profile.claim()
        profile.save()

        messages.success(request, 'Profile updated! Welcome to BAIUST Computer Club.')
        return redirect('member_public', member_uuid=member_uuid)

    return render(request, 'portal/member_claim.html', {'profile': profile})

def logout_view(request):
    logout(request)
    return redirect('home')

def join_guide(request):
    return render(request, 'portal/join_guide.html')

def qr_image_view(request, member_uuid):
    profile = get_object_or_404(Profile, member_uuid=member_uuid, is_member=True)
    if not profile.qr_png:
        raise Http404
    return HttpResponse(profile.qr_png, content_type='image/png')
