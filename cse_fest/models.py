from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Fest(models.Model):
    year = models.IntegerField(unique=True, validators=[MinValueValidator(2020)])
    title = models.CharField(max_length=200, default='CSE Spring Fest')
    is_active = models.BooleanField(default=True)
    target_date = models.DateTimeField(blank=True, null=True, help_text='Countdown target date/time')
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
    team_size = models.PositiveIntegerField(default=1)
    rule_book_pdf = models.FileField(upload_to='cse_fest/rules/', blank=True)
    registration_open = models.BooleanField(default=True)
    requires_team = models.BooleanField(default=False)
    requires_payment = models.BooleanField(default=False)
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
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    event = models.ForeignKey(FestEvent, on_delete=models.CASCADE, related_name='registrations')
    full_name = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    student_id = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    team_name = models.CharField(max_length=200, blank=True, help_text='For group events')
    team_members = models.TextField(blank=True, help_text='Names of team members')
    transaction_id = models.CharField(max_length=100, blank=True, help_text='Payment transaction ID if required')
    notes = models.TextField(blank=True)
    agreed_to_rules = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.event.title}'
