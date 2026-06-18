from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from portal.models import Profile


class Command(BaseCommand):
    help = 'Delete expired member profiles whose membership has ended'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many profiles would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='Only delete profiles that expired at least this many days ago (default: 0 = all expired)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_buffer = options['days']

        qs = Profile.objects.filter(expires_at__isnull=False, expires_at__lt=timezone.now())

        if days_buffer:
            cutoff = timezone.now() - timedelta(days=days_buffer)
            qs = qs.filter(expires_at__lt=cutoff)

        count = qs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired profiles found.'))
            return

        if dry_run:
            self.stdout.write(f'{count} expired profile(s) would be deleted (dry run).')
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired profile(s).'))
