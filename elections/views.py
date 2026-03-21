from rest_framework import generics, permissions
from .models import PoliticalParty, Election, Candidate
from .serializers import (
    PoliticalPartySerializer,
    ElectionSerializer,
    CandidateSerializer,
)


# -------------------------
# Political Parties
# -------------------------
class PoliticalPartyListCreateView(generics.ListCreateAPIView):
    queryset = PoliticalParty.objects.all()
    serializer_class = PoliticalPartySerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can add parties


# -------------------------
# Elections
# -------------------------
class ElectionListView(generics.ListAPIView):
    """
    List all active elections (for users)
    """

    queryset = Election.objects.filter(is_active=True)
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ElectionCreateView(generics.CreateAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------
# Candidates
# -------------------------
class CandidateListCreateView(generics.ListCreateAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        election_id = self.kwargs.get("election_id")

        # Define the desired order of positions
        POSITION_ORDER = ["Governor", "Senator", "Members of the County Assembly"]

        # Fetch candidates for this election
        queryset = Candidate.objects.filter(election_id=election_id)

        # Annotate with a sort index based on POSITION_ORDER
        from django.db.models import Case, When, Value, IntegerField

        order_cases = [
            When(position=pos, then=Value(index)) for index, pos in enumerate(POSITION_ORDER)
        ]

        queryset = queryset.annotate(
            position_order=Case(
                *order_cases,
                default=Value(len(POSITION_ORDER)),  # Other positions come last
                output_field=IntegerField(),
            )
        ).order_by("position_order", "name")  # Sort by position, then name

        return queryset

    def perform_create(self, serializer):
        election_id = self.kwargs.get("election_id")
        election = generics.get_object_or_404(Election, id=election_id)
        serializer.save(election=election)