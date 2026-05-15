from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, EventRegistration

def event_list(request):
    active_events = Event.objects.filter(status='active').order_by('date')
    completed_events = Event.objects.filter(status='completed').order_by('-date')
    return render(request, 'events/event_list.html', {
        'active_events': active_events,
        'completed_events': completed_events,
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = None
    if request.user.is_authenticated:
        registration = EventRegistration.objects.filter(event=event, user=request.user).first()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'registration': registration,
    })

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if not event.registration_open:
        messages.error(request, 'Registration is not open for this event.')
        return redirect('events:event_detail', event_id=event.id)
    
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.error(request, 'You have already registered for this event.')
        return redirect('events:event_detail', event_id=event.id)
    
    EventRegistration.objects.create(event=event, user=request.user)
    messages.success(request, 'Registration submitted successfully! Wait for admin approval.')
    return redirect('events:event_detail', event_id=event.id)
