from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Conversation
from .serializers import ConversationUploadSerializer, ConversationDetailSerializer
from .tasks import process_conversation_task


class ConversationUploadView(APIView):
    parser_classes  = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConversationUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conversation = serializer.save(commercial=request.user)

        process_conversation_task.delay(conversation.id)

        return Response(
            {
                "message":         "Audio received Analyzing in progress",
                "conversation_id": conversation.id,
                "status":          conversation.status,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk, commercial=request.user)
        except Conversation.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)
    

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        convs = Conversation.objects.filter(commercial=request.user)
        serializer = ConversationDetailSerializer(convs, many=True)
        return Response(serializer.data)