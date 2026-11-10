from django.conf import settings
from django.core.management.base import BaseCommand

from portal.models import Profile


class Command(BaseCommand):
    help = 'Generate QR code images for member profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate QR codes that already exist (use after changing DJANGO_BASE_URL)',
        )

    def handle(self, *args, **options):
        qs = Profile.objects.filter(is_member=True)
        if not options['force']:
            qs = qs.filter(qr_png__isnull=True)

        total = qs.count()
        if not total:
            self.stdout.write('No QR codes need generating.')
            return

        self.stdout.write(f'Generating {total} QR code(s) pointing at {settings.BASE_URL}')

        count = 0
        for profile in qs.iterator(chunk_size=100):
            profile.generate_qr_code()
            profile.save(update_fields=['qr_png'])
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Done. Generated {count} QR code(s).'))
