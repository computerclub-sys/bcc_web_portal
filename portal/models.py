from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.fields.related.OneToOneField):
    pass # Wait, let me just subclass models.Model

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True)
    student_id = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, blank=True)
    batch = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
