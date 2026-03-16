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
        return Candidate.objects.filter(election_id=election_id)

    def perform_create(self, serializer):
        election_id = self.kwargs.get("election_id")
        election = generics.get_object_or_404(Election, id=election_id)
        serializer.save(election=election)
