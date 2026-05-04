from celery import shared_task
import openpyxl
from datetime import date
from django.conf import settings
from leads.models import LeadInteresse
import os


@shared_task(bind=True, max_retries=3)
def process_conversation_task(self, conversation_id: int):
    try:
        from conversations.models import Conversation
        from ml.pipeline import process_call

        conv = Conversation.objects.get(id=conversation_id)
        audio_path = conv.audio_file.path

        result = process_call(audio_path)

        conv.transcript     = result["transcript"]
        conv.interest_score = result["score"]
        conv.status = "interested" if result["interested"] else "not_interested"
        conv.save()

        if result["interested"]:
            from leads.models import LeadInteresse
            LeadInteresse.objects.create(
                conversation  = conv,
                client_name  = result.get("name"),
                client_email  = result["email"],
                client_phone  = result["phone"],
            )
            export_excel_task.delay()
        else:
            from leads.models import LeadNonInteresse
            LeadNonInteresse.objects.create(
                conversation=conv,
            )

        return {
            "conversation_id": conversation_id,
            "status":          conv.status,
            "score":           result["score"],
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@shared_task
def export_excel_task():

    headers = ["Nom", "Email", "Telephone", "Score", "Statut", "Date"]

    

    leads = LeadInteresse.objects.filter(
        created_at__date=date.today()
    ).select_related("conversation")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads du jour"

    from openpyxl.styles import Font, PatternFill
    headers = ["Email", "Telephone", "Score", "Statut", "Date"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F3864")

    for lead in leads:
        ws.append([
            lead.client_name  or "",   # add this
            lead.client_email or "",
            lead.client_phone or "",
            f"{lead.conversation.interest_score*100:.1f}%",
            lead.contact_status,
            str(lead.created_at.date()),
        ])

    export_dir = settings.MEDIA_ROOT / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / f"leads_{date.today()}.xlsx"
    wb.save(path)

    return str(path)