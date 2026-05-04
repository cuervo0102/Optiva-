from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Conversation(models.Model):

    STATUS_CHOICES = [
        ("pending",        "En attente"),
        ("processing",     "En cours"),
        ("interested",     "Interesse"),
        ("not_interested", "Pas interesse"),
        ("error",          "Erreur"),
    ]

    commercial     = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="conversations"
    )
    audio_file     = models.FileField(upload_to="audio/%Y/%m/%d/")
    transcript     = models.TextField(blank=True)
    interest_score = models.FloatField(null=True, blank=True)
    status         = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    error_message  = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.commercial} — {self.status} — {self.interest_score}"