from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


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

    @property
    def is_registration_open(self):
        from django.utils import timezone
        if not self.registration_open:
            return False
        if self.last_registration_date and timezone.now() > self.last_registration_date:
            return False
        return True


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
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['date', 'time', 'order']

    def __str__(self):
        return f'{self.title} — {self.fest.year}'


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
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    student_id = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
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
    t_shirt_size = models.CharField(max_length=5, choices=TSHIRT_CHOICES, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.email})'
