from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Fest, FestEvent, FestPrize, FestSchedule, Notice, CommitteeMember, Faq, Sponsor, FestRegistration, FestTeamMember


def _get_fest(year):
    return get_object_or_404(Fest, year=year)


def redirect_to_latest(request):
    fest = Fest.objects.filter(is_active=True).first()
    if not fest:
        fest = Fest.objects.order_by('-year').first()
    if fest:
        return redirect('cse_fest:index', year=fest.year)
    return redirect('/')


def index(request, year):
    fest = _get_fest(year)
    events = FestEvent.objects.filter(fest=fest).order_by('order')
    schedules = FestSchedule.objects.filter(fest=fest).order_by('order', 'date', 'time')
    notices = Notice.objects.filter(fest=fest, is_active=True)
    committee = CommitteeMember.objects.filter(fest=fest).order_by('order')
    faqs = Faq.objects.filter(fest=fest, is_active=True)
    sponsors = Sponsor.objects.filter(fest=fest).order_by('order')

    return render(request, 'cse_fest/index.html', {
        'fest': fest,
        'events': events,
        'schedules': schedules,
        'notices': notices,
        'committee': committee,
        'faqs': faqs,
        'sponsors': sponsors,
    })


def event_detail(request, year, slug):
    fest = _get_fest(year)
    event = get_object_or_404(FestEvent, fest=fest, slug=slug)
    prizes = FestPrize.objects.filter(event=event).order_by('order')

    return render(request, 'cse_fest/event_detail.html', {
        'fest': fest,
        'event': event,
        'prizes': prizes,
    })


def register(request, year):
    fest = _get_fest(year)

    if request.method != 'POST':
        return redirect('cse_fest:index', year=year)

    event_id = request.POST.get('event_id')
    event = get_object_or_404(FestEvent, id=event_id, fest=fest)

    if not event.is_registration_open:
        messages.error(request, 'Registration is closed for this event.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()

    is_iupc = event.category == 'iupc'
    is_hackathon = event.category == 'hackathon'

    if is_iupc:
        full_name = request.POST.get('tl_name', '').strip()
        email = request.POST.get('tl_email', '').strip()
        phone = request.POST.get('tl_phone', '').strip()

    if is_hackathon:
        full_name = request.POST.get('tl_name', '').strip()
        email = request.POST.get('tl_email', '').strip()
        phone = request.POST.get('tl_phone', '').strip()

    if not full_name or not email or not phone:
        messages.error(request, 'Name, email, and phone are required.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    if not request.POST.get('agreed_to_rules'):
        messages.error(request, 'You must agree to the rules & regulations.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    payment_method = request.POST.get('payment_method', 'physical')
    if payment_method == 'bkash' and not request.POST.get('transaction_id', '').strip():
        messages.error(request, 'Transaction ID is required for bKash payment.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    registration = FestRegistration.objects.create(
        event=event,
        full_name=full_name,
        university='BAIUST',
        department=request.POST.get('department', '') if not is_iupc else '',
        student_id=request.POST.get('student_id', '') if not is_iupc else '',
        email=email,
        phone=phone,
        gender=request.POST.get('gender', ''),
        team_name=request.POST.get('team_name', '') if not is_hackathon else request.POST.get('hackathon_team_name', ''),
        hackathon_category=request.POST.get('hackathon_category', '') if is_hackathon else '',
        payment_method=request.POST.get('payment_method', 'physical'),
        transaction_id=request.POST.get('transaction_id', ''),
        in_game_name_id=request.POST.get('in_game_name_id', ''),
        device_name=request.POST.get('device_name', ''),
        self_photo=request.FILES.get('self_photo'),
        notes=request.POST.get('notes', ''),
        agreed_to_rules=True,
    )

    if is_hackathon or is_iupc:
        seen_names = set()
        seen_ids = set()
        count = 4 if is_hackathon else 3
        for i in range(1, count + 1):
            tm_name = request.POST.get(f'member_{i}_name', '').strip()
            tm_id = request.POST.get(f'member_{i}_student_id', '').strip()
            if tm_name:
                if tm_name.lower() in seen_names:
                    messages.error(request, f'Duplicate member name: {tm_name}. Each member must be unique.')
                    return redirect('cse_fest:event_detail', year=year, slug=event.slug)
                seen_names.add(tm_name.lower())
                if tm_id:
                    if tm_id.lower() in seen_ids:
                        messages.error(request, f'Duplicate student ID: {tm_id}. Each member must have a unique ID.')
                        return redirect('cse_fest:event_detail', year=year, slug=event.slug)
                    seen_ids.add(tm_id.lower())

    if is_hackathon:
        for i in range(1, 5):
            tm_name = request.POST.get(f'member_{i}_name', '').strip()
            if tm_name:
                FestTeamMember.objects.create(
                    registration=registration,
                    name=tm_name,
                    email=request.POST.get(f'member_{i}_email', ''),
                    phone=request.POST.get(f'member_{i}_phone', ''),
                    student_id=request.POST.get(f'member_{i}_student_id', ''),
                    department=request.POST.get(f'member_{i}_department', ''),
                    semester=request.POST.get(f'member_{i}_semester', ''),
                    t_shirt_size=request.POST.get(f'member_{i}_t_shirt', ''),
                )
    elif is_iupc:
        for i in range(1, 4):
            tm_name = request.POST.get(f'member_{i}_name', '').strip()
            if tm_name:
                FestTeamMember.objects.create(
                    registration=registration,
                    name=tm_name,
                    email='',
                    phone=request.POST.get(f'member_{i}_phone', ''),
                    student_id=request.POST.get(f'member_{i}_student_id', ''),
                    department=request.POST.get(f'member_{i}_department', ''),
                    semester=request.POST.get(f'member_{i}_semester', ''),
                    t_shirt_size=request.POST.get(f'member_{i}_t_shirt', ''),
                )
    elif event.requires_team:
        try:
            team_size = int(request.POST.get('team_size', 0))
        except (ValueError, TypeError):
            team_size = 0
        for i in range(team_size):
            tm_name = request.POST.get(f'team_member_name_{i}', '').strip()
            tm_email = request.POST.get(f'team_member_email_{i}', '').strip()
            if tm_name and tm_email:
                FestTeamMember.objects.create(
                    registration=registration,
                    name=tm_name,
                    email=tm_email,
                )

    team_members = list(registration.team_members.all())

    try:
        subject = f'Application Received — {event.title} ({fest.title})'
        logo_url = settings.BASE_URL + settings.STATIC_URL + 'portal/images/BCC_Club_logo.png'
        html = render_to_string('cse_fest/emails/confirmation.html', {
            'name': full_name,
            'event': event,
            'fest': fest,
            'registration': registration,
            'team_members': team_members,
            'logo_url': logo_url,
        })
        email = EmailMultiAlternatives(
            subject,
            strip_tags(html),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
            headers={'List-Unsubscribe': f'<{settings.BASE_URL}>', 'X-Mailer': 'BAIUST Computer Club'},
        )
        email.attach_alternative(html, 'text/html')
        email.send(fail_silently=True)
    except Exception:
        pass

    messages.success(request, f'Registration successful! Your application ID is {registration.application_id}. Check your email ({email}) for confirmation.')
    return redirect('cse_fest:event_detail', year=year, slug=event.slug)


def application_status(request, year):
    fest = _get_fest(year)
    registrations = None
    search_id = ''
    search_type = 'id'

    if request.method == 'POST':
        search_type = request.POST.get('search_type', 'id')
        search_id = request.POST.get('application_id', '').strip()
        if search_id:
            if search_type == 'team':
                registrations = FestRegistration.objects.filter(
                    event__fest=fest,
                    team_name__icontains=search_id,
                ).select_related('event').order_by('-created_at')
                if not registrations:
                    messages.error(request, 'No applications found with that team name.')
            else:
                try:
                    reg = FestRegistration.objects.get(application_id=search_id, event__fest=fest)
                    registrations = [reg]
                except FestRegistration.DoesNotExist:
                    messages.error(request, 'No application found with that ID.')

    return render(request, 'cse_fest/application_status.html', {
        'fest': fest,
        'registrations': registrations,
        'search_id': search_id,
        'search_type': search_type,
    })


def invitation(request, year):
    fest = _get_fest(year)
    return render(request, 'cse_fest/invitation.html', {
        'fest': fest,
    })
