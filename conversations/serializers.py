from rest_framework import serializers
from .models import Conversation


class ConversationUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Conversation
        fields = ["id", "audio_file", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Conversation
        fields = [
            "id", "audio_file", "transcript",
            "interest_score", "status", "error_message",
            "created_at", "updated_at",
        ]
        read_only_fields = fields