from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import date
import os

from .models import LeadInteresse, LeadNonInteresse
from .serializers import LeadInteresseSerializer
from users.permissions import IsAssistantOrManager, IsAnalystOrManager
from conversations.models import Conversation


class InterestedLeadsView(APIView):
    permission_classes = [IsAuthenticated, IsAssistantOrManager]

    def get(self, request):
        filter_date = request.query_params.get("date", str(date.today()))
        commercial_id = request.query_params.get("commercial_id")

        leads = LeadInteresse.objects.select_related(
            "conversation", "conversation__commercial"
        ).filter(created_at__date=filter_date)

        if commercial_id:
            leads = leads.filter(conversation__commercial_id=commercial_id)

        serializer = LeadInteresseSerializer(leads, many=True)
        return Response({
            "date":  filter_date,
            "count": leads.count(),
            "leads": serializer.data,
        })


class ExportLeadsView(APIView):
    permission_classes = [IsAuthenticated, IsAssistantOrManager]

    def get(self, request):
        from django.conf import settings
        filter_date = request.query_params.get("date", str(date.today()))
        path = settings.MEDIA_ROOT / "exports" / f"leads_{filter_date}.xlsx"

        if not os.path.exists(path):
            from conversations.tasks import export_excel_task
            export_excel_task.apply() 
            if not os.path.exists(path):
                return Response(
                    {"error": f"No export found for {filter_date}."},
                    status=404
                )

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=f"leads_{filter_date}.xlsx"
        )


class AllLeadsView(APIView):
    permission_classes = [IsAuthenticated, IsAnalystOrManager]

    def get(self, request):
        interested = LeadInteresse.objects.select_related(
            "conversation", "conversation__commercial"
        ).all()
        not_interested = LeadNonInteresse.objects.select_related(
            "conversation", "conversation__commercial"
        ).count()

        serializer = LeadInteresseSerializer(interested, many=True)
        return Response({
            "total_interested":     interested.count(),
            "total_not_interested": not_interested,
            "leads":                serializer.data,
        })


class AnalyticsSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAnalystOrManager]

    def get(self, request):
        total_conversations = Conversation.objects.count()
        total_interested    = LeadInteresse.objects.count()
        total_not_interested = LeadNonInteresse.objects.count()
        avg_score = Conversation.objects.filter(
            interest_score__isnull=False
        ).aggregate(avg=Avg("interest_score"))["avg"] or 0

        commercials = Conversation.objects.values(
            "commercial__id",
            "commercial__full_name",    
            "commercial__username",     
            "commercial__matricule",
            "commercial__first_name",
            "commercial__last_name",
        ).annotate(
            total=Count("id"),
            interested=Count("id", filter=Q(status="interested")),
            not_interested=Count("id", filter=Q(status="not_interested")),
            avg_score=Avg("interest_score"),
        ).order_by("-total")

        from django.db.models.functions import TruncDate
        per_day = Conversation.objects.annotate(
            day=TruncDate("created_at")
        ).values("day").annotate(
            total=Count("id"),
            interested=Count("id", filter=Q(status="interested")),
        ).order_by("day")

        return Response({
            "total_conversations":  total_conversations,
            "total_interested":     total_interested,
            "total_not_interested": total_not_interested,
            "conversion_rate":      round(total_interested / total_conversations * 100, 1) if total_conversations else 0,
            "avg_score":            round(avg_score * 100, 1),
            "per_commercial":       list(commercials),
            "per_day":              list(per_day),
        })