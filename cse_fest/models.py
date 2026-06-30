from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import os


class Fest(models.Model):
    year = models.IntegerField(unique=True, validators=[MinValueValidator(2020)])
    title = models.CharField(max_length=200, default='CSE Spring Fest')
    is_active = models.BooleanField(default=True)
    target_date = models.DateTimeField(blank=True, null=True, help_text='Countdown target date/time')
    bkash_number = models.CharField(max_length=20, blank=True, help_text='bKash number for payment')
    poster = models.ImageField(upload_to='cse_fest/posters/', blank=True, help_text='Fest poster for homepage card')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f'{self.title} {self.year}'


class FestEvent(models.Model):
    CATEGORY_CHOICES = [
        ('hackathon', 'Hackathon'),
        ('iupc', 'IUPC'),
        ('efootball', 'E-Football'),
        ('ictquiz', 'ICT Quiz'),
    ]

    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    poster = models.ImageField(upload_to='cse_fest/posters/', blank=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rule_book_pdf = models.URLField(blank=True, help_text='Google Drive link to the rule book PDF')
    registration_open = models.BooleanField(default=True)
    requires_team = models.BooleanField(default=False)
    min_team_size = models.PositiveIntegerField(default=1)
    max_team_size = models.PositiveIntegerField(default=1)
    requires_payment = models.BooleanField(default=False)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, help_text='Registration fee in BDT')
    last_registration_date = models.DateTimeField(blank=True, null=True, help_text='Last date/time for registration (per event)')
    hackathon_fee_3 = models.DecimalField(max_digits=10, decimal_places=2, default=1500, blank=True, help_text='Hackathon fee for 3-member team')
    hackathon_fee_4 = models.DecimalField(max_digits=10, decimal_places=2, default=2000, blank=True, help_text='Hackathon fee for 4-member team')
    prize_pool = models.CharField(max_length=200, blank=True, help_text='e.g. 50,000 BDT + Trophies')
    provided_kit = models.TextField(blank=True, help_text='Items provided to participants (T-shirt, food, certificate, etc.)')
    primary_color = models.CharField(max_length=7, blank=True, help_text='Auto-extracted dominant color from poster')
    secondary_color = models.CharField(max_length=7, blank=True, help_text='Auto-extracted secondary color from poster')
    accent_color = models.CharField(max_length=7, blank=True, help_text='Auto-extracted accent color from poster')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('fest', 'slug')
        ordering = ['order']

    def __str__(self):
        return f'{self.title} — {self.fest.year}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def _extract_colors(self, path_or_url):
        from PIL import Image
        import tempfile, os, requests
        tmp_path = None
        try:
            if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
                r = requests.get(path_or_url, timeout=15)
                r.raise_for_status()
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                tmp.write(r.content)
                tmp.close()
                tmp_path = tmp.name
                img = Image.open(tmp_path)
            else:
                img = Image.open(path_or_url)
            img = img.convert('RGB')
            img.load()
            img = img.resize((4, 4), Image.LANCZOS)
            pixels = list(img.getdata())
            counts = {}
            for r, g, b in pixels:
                key = (r // 64 * 64, g // 64 * 64, b // 64 * 64)
                avg = (key[0] + 32, key[1] + 32, key[2] + 32)
                counts[avg] = counts.get(avg, 0) + 1
            sorted_colors = sorted(counts.items(), key=lambda x: -x[1])
            def to_hex(rgb):
                return '#{:02x}{:02x}{:02x}'.format(
                    min(255, max(0, rgb[0])),
                    min(255, max(0, rgb[1])),
                    min(255, max(0, rgb[2]))
                )
            if not sorted_colors:
                return None
            primary = to_hex(sorted_colors[0][0])
            secondary = to_hex(sorted_colors[1][0]) if len(sorted_colors) > 1 else primary
            accent = to_hex(sorted_colors[2][0]) if len(sorted_colors) > 2 else secondary
            return (primary, secondary, accent)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @property
    def is_registration_open(self):
        from django.utils import timezone
        if not self.registration_open:
            return False
        if self.last_registration_date and timezone.now() > self.last_registration_date:
            return False
        return True

    @property
    def theme_colors(self):
        if self.primary_color:
            primary = self.primary_color
            secondary = self.secondary_color or self.primary_color
            accent = self.accent_color or self.primary_color
        else:
            defaults = {
                'hackathon': ('#ea580c', '#dc2626', '#f97316'),
                'iupc': ('#7c3aed', '#4f46e5', '#a855f7'),
                'efootball': ('#059669', '#047857', '#10b981'),
                'ictquiz': ('#0284c7', '#0369a1', '#38bdf8'),
            }
            d = defaults.get(self.category, ('#d946ef', '#a21caf', '#e879f9'))
            primary, secondary, accent = d
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return f'{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}'
        return {
            'primary': primary,
            'secondary': secondary,
            'accent': accent,
            'accent_rgb': hex_to_rgb(accent),
            'secondary_rgb': hex_to_rgb(secondary),
        }


class FestPrize(models.Model):
    event = models.ForeignKey(FestEvent, on_delete=models.CASCADE, related_name='prizes')
    position = models.CharField(max_length=100, help_text='e.g. Winner, 1st Runners Up')
    amount = models.CharField(max_length=200, help_text='e.g. 1500/- & Trophy')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.position} — {self.event.title}'


class FestSchedule(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='schedules')
    event = models.ForeignKey(FestEvent, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules')
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        label = f'{self.title} — {self.fest.year}'
        if self.event:
            label += f' ({self.event.title})'
        return label


class Notice(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='notices')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CommitteeMember(models.Model):
    ROLE_CHOICES = [
        ('chief_guest', 'Chief Guest'),
        ('advisor', 'Advisor'),
        ('organizer', 'Organizing Committee'),
        ('problem_setter', 'Problem Setter'),
        ('volunteer', 'Volunteer'),
    ]

    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='committee_members')
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='cse_fest/committee/', blank=True)
    position = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=200, blank=True)
    contact = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.name} — {self.get_role_display()} ({self.fest.year})'


class Faq(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


class Sponsor(models.Model):
    SPONSOR_TYPE_CHOICES = [
        ('university', 'University Partner'),
        ('tech', 'Tech Partner'),
        ('gold', 'Gold Sponsor'),
        ('silver', 'Silver Sponsor'),
    ]

    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='sponsors')
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='cse_fest/sponsors/')
    sponsor_type = models.CharField(max_length=20, choices=SPONSOR_TYPE_CHOICES)
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.name} ({self.get_sponsor_type_display()})'


class FestRegistration(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('physical', 'Physical Payment'),
        ('bkash', 'bKash'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    event = models.ForeignKey(FestEvent, on_delete=models.CASCADE, related_name='registrations')
    application_id = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    full_name = models.CharField(max_length=200)
    university = models.CharField(max_length=200, blank=True, default='BAIUST')
    department = models.CharField(max_length=200, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    section = models.CharField(max_length=5, blank=True, choices=[('A','A'),('B','B'),('C','C')])
    group = models.CharField(max_length=5, blank=True, choices=[('G1','G1'),('G2','G2')])
    team_name = models.CharField(max_length=200, blank=True, help_text='For group events')
    hackathon_category = models.CharField(max_length=100, blank=True, help_text='Project category (for hackathon)')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='physical')
    transaction_id = models.CharField(max_length=100, blank=True, help_text='bKash transaction ID')
    in_game_name_id = models.CharField(max_length=200, blank=True, help_text='In-Game Name & ID (for eFootball)')
    device_name = models.CharField(max_length=200, blank=True, help_text='Device Name (for eFootball)')
    self_photo = models.ImageField(upload_to='cse_fest/selfies/', blank=True, help_text='Self photo (for eFootball)')
    notes = models.TextField(blank=True)
    agreed_to_rules = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.application_id:
            prefix = f'CSE-{self.event.fest.year}'
            last = FestRegistration.objects.filter(application_id__startswith=prefix).order_by('-id').first()
            if last and last.application_id:
                num = int(last.application_id.split('-')[-1]) + 1
            else:
                num = 1
            self.application_id = f'{prefix}-{num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.application_id} — {self.full_name} — {self.event.title}'


class FestTeamMember(models.Model):
    TSHIRT_CHOICES = [
        ('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL'), ('xxl', 'XXL'),
    ]

    registration = models.ForeignKey(FestRegistration, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=200, blank=True)
    semester = models.CharField(max_length=20, blank=True, help_text='e.g. 4/1')
    section = models.CharField(max_length=5, blank=True, choices=[('A','A'),('B','B'),('C','C')])
    group = models.CharField(max_length=5, blank=True, choices=[('G1','G1'),('G2','G2')])
    t_shirt_size = models.CharField(max_length=5, choices=TSHIRT_CHOICES, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.email})'
