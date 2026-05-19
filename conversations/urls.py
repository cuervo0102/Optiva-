from django.urls import path
from .views import ConversationUploadView, ConversationDetailView, ConversationListView

urlpatterns = [
    path("",          ConversationListView.as_view(),  name="conversation-list"),
    path("upload/",   ConversationUploadView.as_view(), name="conversation-upload"),
    path("<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
]