from django.contrib.auth.models import AbstractUser
from django.db import models
import os


def profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"profile_{instance.username}.{ext}"
    return os.path.join('profiles', filename)


class User(AbstractUser):

    ROLES = [
        ("commercial",  "Commercial"),
        ("assistant",   "Assistant Commercial"),
        ("analyst",     "Data Analyst"),
        ("manager",     "Manager"),
        ("admin",       "Administrateur"),
    ]

    role = models.CharField(
        max_length=20, choices=ROLES, default="commercial"
    )

    full_name  = models.CharField(max_length=255, blank=True)
    phone      = models.CharField(max_length=20,  blank=True)
    photo      = models.ImageField(
        upload_to=profile_upload_path,
        null=True, blank=True
    )

    matricule  = models.CharField(
        max_length=50, unique=True,
        null=True, blank=True
    )
    cnss = models.CharField(
        max_length=50, unique=True,
        null=True, blank=True
    )
    department = models.CharField(max_length=100, blank=True)
    hire_date  = models.DateField(null=True, blank=True)

    failed_login_attempts = models.IntegerField(default=0)
    last_login_ip         = models.GenericIPAddressField(null=True, blank=True)
    is_locked             = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.matricule} — {self.full_name} ({self.role})"

    def save(self, *args, **kwargs):
        if self.first_name or self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

    @property
    def is_commercial(self):  return self.role == "commercial"
    @property
    def is_assistant(self):   return self.role == "assistant"
    @property
    def is_analyst(self):     return self.role == "analyst"
    @property
    def is_manager(self):     return self.role == "manager"