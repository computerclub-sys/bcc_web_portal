from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Fest, FestEvent, FestSchedule, Notice, CommitteeMember, Faq, Sponsor, FestRegistration


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
    schedules = FestSchedule.objects.filter(fest=fest).order_by('date', 'time')
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

    return render(request, 'cse_fest/event_detail.html', {
        'fest': fest,
        'event': event,
    })


def register(request, year):
    fest = _get_fest(year)

    if request.method != 'POST':
        return redirect('cse_fest:index', year=year)

    event_id = request.POST.get('event_id')
    event = get_object_or_404(FestEvent, id=event_id, fest=fest)

    if not event.registration_open:
        messages.error(request, 'Registration is closed for this event.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()

    if not full_name or not email or not phone:
        messages.error(request, 'Name, email, and phone are required.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    if not request.POST.get('agreed_to_rules'):
        messages.error(request, 'You must agree to the rules & regulations.')
        return redirect('cse_fest:event_detail', year=year, slug=event.slug)

    registration = FestRegistration.objects.create(
        event=event,
        full_name=full_name,
        university=request.POST.get('university', ''),
        department=request.POST.get('department', ''),
        student_id=request.POST.get('student_id', ''),
        email=email,
        phone=phone,
        gender=request.POST.get('gender', ''),
        team_name=request.POST.get('team_name', ''),
        team_members=request.POST.get('team_members', ''),
        transaction_id=request.POST.get('transaction_id', ''),
        notes=request.POST.get('notes', ''),
        agreed_to_rules=True,
    )

    try:
        subject = f'Registration Confirmed — {event.title} ({fest.title})'
        html = render_to_string('cse_fest/emails/confirmation.html', {
            'name': full_name,
            'event': event,
            'fest': fest,
            'registration': registration,
        })
        send_mail(
            subject,
            strip_tags(html),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html,
            fail_silently=True,
        )
    except Exception:
        pass

    messages.success(request, f'Registration successful! Check your email ({email}) for confirmation.')
    return redirect('cse_fest:event_detail', year=year, slug=event.slug)
