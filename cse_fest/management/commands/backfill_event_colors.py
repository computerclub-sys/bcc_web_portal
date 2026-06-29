from django.core.management.base import BaseCommand
from cse_fest.models import FestEvent


class Command(BaseCommand):
    help = 'Extract dominant colors from event posters that lack them'

    def handle(self, *args, **options):
        qs = FestEvent.objects.filter(
            poster__isnull=False
        ).exclude(
            poster=''
        ).filter(
            primary_color=''
        )
        count = qs.count()
        if not count:
            self.stdout.write('No events need backfilling.')
            return

        for e in qs:
            old = (e.primary_color, e.secondary_color, e.accent_color)
            e.save()
            if (e.primary_color, e.secondary_color, e.accent_color) != old:
                self.stdout.write(
                    f'{e.title}: {e.primary_color} / {e.secondary_color} / {e.accent_color}'
                )
            else:
                self.stdout.write(self.style.WARNING(f'{e.title}: could not extract'))

        self.stdout.write(self.style.SUCCESS(f'Processed {count} events'))
