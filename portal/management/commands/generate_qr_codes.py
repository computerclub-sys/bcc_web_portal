from django.core.management.base import BaseCommand
from portal.models import Profile

class Command(BaseCommand):
    help = 'Generate QR code images for all approved general members'

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(is_member=True, qr_png__isnull=True)
        count = 0
        for profile in profiles:
            profile.generate_qr_code()
            profile.save(update_fields=['qr_png'])
            count += 1
            self.stdout.write(f'  Generated QR for {profile}')
        self.stdout.write(self.style.SUCCESS(f'Done. Generated {count} QR code(s).'))
