from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import FestRegistration


@receiver(pre_save, sender=FestRegistration)
def stash_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = FestRegistration.objects.get(pk=instance.pk).status
        except FestRegistration.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=FestRegistration)
def send_confirmation_email(sender, instance, created, **kwargs):
    old = getattr(instance, '_old_status', None)
    if not created and old != 'confirmed' and instance.status == 'confirmed':
        event = instance.event
        fest = event.fest
        team_members = list(instance.team_members.all())

        subject = f'Registration Approved — {event.title} ({fest.title})'
        html = render_to_string('cse_fest/emails/confirmation.html', {
            'name': instance.full_name,
            'event': event,
            'fest': fest,
            'registration': instance,
            'team_members': team_members,
        })
        send_mail(
            subject,
            strip_tags(html),
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            html_message=html,
            fail_silently=True,
        )
