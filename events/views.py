from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Event, EventRegistration

def event_list(request):
    active_events = Event.objects.filter(status='active').order_by('date')
    completed_events = Event.objects.filter(status='completed').order_by('-date')
    paginator = Paginator(completed_events, 6)
    page_number = request.GET.get('page')
    completed_page = paginator.get_page(page_number)
    return render(request, 'events/event_list.html', {
        'active_events': active_events,
        'completed_events': completed_page,
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
    
    if not event.requires_registration:
        messages.info(request, 'This event is open to all. No registration needed.')
        return redirect('events:event_detail', event_id=event.id)
    
    if not event.registration_open:
        messages.error(request, 'Registration is not open for this event.')
        return redirect('events:event_detail', event_id=event.id)
    
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.error(request, 'You have already registered for this event.')
        return redirect('events:event_detail', event_id=event.id)
    
    if request.method == 'POST':
        if event.requires_payment:
            payment_method = request.POST.get('payment_method', 'bkash')
            transaction_id = request.POST.get('transaction_id', '')
            
            if payment_method == 'bkash' and not transaction_id:
                messages.error(request, 'Transaction ID is required for bKash payment.')
                return redirect('events:event_detail', event_id=event.id)
            
            EventRegistration.objects.create(
                event=event,
                user=request.user,
                payment_method=payment_method,
                transaction_id=transaction_id
            )
        else:
            EventRegistration.objects.create(
                event=event,
                user=request.user,
                payment_method='offline',
                transaction_id='',
                payment_status='approved',
                payment_reviewed_at=timezone.now(),
                payment_reviewed_by=request.user
            )
        
        messages.success(request, 'Registration submitted successfully! Wait for admin approval.')
        return redirect('events:event_detail', event_id=event.id)
    
    return redirect('events:event_detail', event_id=event.id)
