from django.core.management.base import BaseCommand
from cse_fest.models import FestEvent
import traceback


class Command(BaseCommand):
    help = 'Debug color extraction for event posters'

    def handle(self, *args, **options):
        qs = FestEvent.objects.filter(
            poster__isnull=False
        ).exclude(
            poster=''
        ).filter(
            primary_color=''
        )
        count = qs.count()
        self.stdout.write(f'Found {count} events without colors')

        for e in qs:
            self.stdout.write(f'\n--- {e.title} ---')
            self.stdout.write(f'  poster field: {e.poster!r}')
            try:
                self.stdout.write(f'  poster.path: {e.poster.path}')
            except Exception as ex:
                self.stdout.write(f'  poster.path ERROR: {ex}')
            try:
                self.stdout.write(f'  poster.url: {e.poster.url}')
            except Exception as ex:
                self.stdout.write(f'  poster.url ERROR: {ex}')

            try:
                path_or_url = e.poster.url
                self.stdout.write(f'  extracting from: {path_or_url}')
                import requests
                r = requests.get(path_or_url, timeout=15)
                self.stdout.write(f'  HTTP status: {r.status_code}')
                self.stdout.write(f'  content length: {len(r.content)}')
                if r.status_code == 200:
                    from PIL import Image
                    import tempfile
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    tmp.write(r.content)
                    tmp.close()
                    img = Image.open(tmp.name)
                    self.stdout.write(f'  image size: {img.size}, mode: {img.mode}')
                    import os
                    os.unlink(tmp.name)
                else:
                    self.stdout.write(self.style.ERROR(f'  HTTP error: {r.text[:200]}'))
            except Exception as ex:
                self.stdout.write(self.style.ERROR(f'  EXTRACTION ERROR: {ex}'))
                self.stdout.write(traceback.format_exc())
