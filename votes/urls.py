from django.urls import path
from .views import CastVoteView, ElectionResultsView

urlpatterns = [
    path(
        "cast/<int:position_id>/<int:candidate_id>/",
        CastVoteView.as_view(),
        name="cast_vote",
    ),
    path(
        "results/<int:election_id>/",
        ElectionResultsView.as_view(),
        name="election_results",
    ),
]
