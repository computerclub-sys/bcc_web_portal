import uuid
from datetime import timedelta
from io import BytesIO

import qrcode
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    student_id = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, blank=True)
    batch = models.CharField(max_length=50, blank=True)
    is_member = models.BooleanField(default=False)
    member_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_png = models.BinaryField(null=True, blank=True, editable=False)
    claimed_at = models.DateTimeField(null=True, blank=True, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True, editable=False)

    MEMBERSHIP_DURATION_YEARS = 4

    @property
    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def claim(self):
        self.claimed_at = timezone.now()
        self.expires_at = self.claimed_at + timedelta(days=365 * self.MEMBERSHIP_DURATION_YEARS)

    def generate_qr_code(self):
        from django.conf import settings
        url = f'{settings.BASE_URL}/member/{self.member_uuid}/'
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.qr_png = buffer.getvalue()
        buffer.close()

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s profile"
        return f"Unclaimed ({self.student_id or self.member_uuid})"


class TeamMember(models.Model):
    PANEL_CHOICES = [
        ('advisory', 'Advisory Panel'),
        ('leading', 'Leading Panel'),
        ('tech', 'Tech Panel'),
        ('social_media', 'Social Media & Relations Panel'),
        ('treasurer', 'Treasurer Panel'),
        ('organizing', 'Organizing Panel'),
        ('executive', 'Executive Members'),
    ]

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=50, blank=True, default='CSE')
    panel = models.CharField(max_length=20, choices=PANEL_CHOICES)
    bio = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    badge = models.CharField(max_length=50, blank=True)
    avatar_letter = models.CharField(max_length=1, blank=True)
    image = models.ImageField(upload_to='team/', blank=True)
    email = models.EmailField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['panel', 'order']

    def __str__(self):
        return self.name
