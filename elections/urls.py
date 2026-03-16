from django.urls import path
from .views import (
    PoliticalPartyListCreateView,
    ElectionListView,
    ElectionCreateView,
    CandidateListCreateView,
)

urlpatterns = [
    # Parties
    path("parties/", PoliticalPartyListCreateView.as_view(), name="party-list-create"),
    # Elections
    path("elections/", ElectionListView.as_view(), name="election-list"),
    path("elections/create/", ElectionCreateView.as_view(), name="election-create"),
    # Candidates
    path(
        "elections/<int:election_id>/candidates/",
        CandidateListCreateView.as_view(),
        name="candidate-list-create",
    ),
]
