from django.db import models
from conversations.models import Conversation


class LeadInteresse(models.Model):
    
    CONTACT_STATUS_CHOICES = [
        ("to_contact", "To contact"),
        ("contacted", "Contacted"),
        ("converted", "Converted"),
        ("lost", "Lost"),
    ]

    client_name = models.CharField(max_length=100, blank=True, null=True)
    conversation   = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="lead_interesse")
    client_email   = models.EmailField(blank=True, null=True)
    client_phone   = models.CharField(max_length=20, blank=True, null=True)
    contact_status = models.CharField(max_length=20, choices=CONTACT_STATUS_CHOICES, default="to_contact")
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead Interested"

    def __str__(self):
        return f"Lead {self.conversation.id} — {self.client_email or self.client_phone}"


class LeadNonInteresse(models.Model):

    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="lead_non_interesse")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead Non Interested"

    def __str__(self):
        return f"Lead non interested — conversation {self.conversation.id}"