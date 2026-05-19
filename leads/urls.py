from django.urls import path
from .views import (
    InterestedLeadsView,
    ExportLeadsView,
    AllLeadsView,
    AnalyticsSummaryView,
)

urlpatterns = [
    path("interested/",        InterestedLeadsView.as_view(),   name="leads-interested"),
    path("export/",            ExportLeadsView.as_view(),        name="leads-export"),
    path("all/",               AllLeadsView.as_view(),           name="leads-all"),
    path("analytics/summary/", AnalyticsSummaryView.as_view(),  name="analytics-summary"),
]