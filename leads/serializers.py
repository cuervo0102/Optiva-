from rest_framework import serializers
from .models import LeadInteresse, LeadNonInteresse


class LeadInteresseSerializer(serializers.ModelSerializer):
    commercial_name = serializers.CharField(
        source='conversation.commercial.full_name', read_only=True)
    commercial_matricule = serializers.CharField(
        source='conversation.commercial.matricule', read_only=True)
    score = serializers.FloatField(
        source='conversation.interest_score', read_only=True)
    conversation_date = serializers.DateTimeField(
        source='conversation.created_at', read_only=True)

    class Meta:
        model  = LeadInteresse
        fields = [
            "id", "client_name", "client_email", "client_phone",
            "contact_status", "score", "commercial_name",
            "commercial_matricule", "conversation_date", "created_at",
        ]


class LeadNonInteresseSerializer(serializers.ModelSerializer):
    commercial_name = serializers.CharField(
        source='conversation.commercial.full_name', read_only=True)
    score = serializers.FloatField(
        source='conversation.interest_score', read_only=True)
    conversation_date = serializers.DateTimeField(
        source='conversation.created_at', read_only=True)

    class Meta:
        model  = LeadNonInteresse
        fields = [
            "id", "commercial_name", "score",
            "conversation_date", "created_at",
        ]