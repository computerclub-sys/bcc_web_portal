from django.core.management.base import BaseCommand
from portal.models import Profile


class Command(BaseCommand):
    help = 'Create initial pre-claimed member profiles with QR codes'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=600, help='Number of profiles to create')
        parser.add_argument('--prefix', type=str, default='BCC', help='Student ID prefix')
        parser.add_argument('--start', type=int, default=1, help='Starting number')

    def handle(self, *args, **options):
        count = options['count']
        prefix = options['prefix']
        start = options['start']

        existing = Profile.objects.filter(is_member=True, user__isnull=True).count()
        if existing > 0:
            self.stdout.write(f'Found {existing} unclaimed member profiles already exist.')
            self.stdout.write(self.style.WARNING('Delete them first or use a different approach.'))
            return

        for i in range(start, start + count):
            sid = f'{prefix}-{i:04d}'
            profile = Profile.objects.create(
                student_id=sid,
                is_member=True,
            )
            profile.generate_qr_code()
            profile.save(update_fields=['qr_png'])

            if i % 100 == 0:
                self.stdout.write(f'  Created {i - start + 1}/{count}...')

        self.stdout.write(self.style.SUCCESS(
            f'Created {count} member profiles.'
        ))
