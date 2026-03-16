from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from elections.models import Candidate, Election
from .models import Vote
from .serializers import VoteSerializer
from django.db import transaction
from elections.models import Candidate, Position


class CastVoteView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, position_id, candidate_id):
        voter = request.user

        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            return Response(
                {"error": "Position not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            candidate = Candidate.objects.select_for_update().get(id=candidate_id)
        except Candidate.DoesNotExist:
            return Response(
                {"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Ensure the candidate belongs to this position
        if candidate.position_id != position.id:
            return Response(
                {"error": "Candidate does not belong to this position"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent user from voting twice for the same position
        if Vote.objects.filter(voter=voter, position=position).exists():
            return Response(
                {"error": "You have already voted for this position"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the vote
        vote = Vote.objects.create(voter=voter, position=position, candidate=candidate)

        # Increment candidate votes
        candidate.votes += 1
        candidate.save(update_fields=["votes"])

        serializer = VoteSerializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from elections.models import Election, Position


class ElectionResultsView(APIView):
    permission_classes = [IsAuthenticated]  # Optional: can set to AllowAny if public

    def get(self, request, election_id):
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return Response({"error": "Election not found"}, status=404)

        positions_data = []
        for position in election.positions.all():
            candidates = position.candidates.all().order_by(
                "-votes"
            )  # sort by votes descending
            candidates_data = []
            for candidate in candidates:
                candidates_data.append(
                    {
                        "candidate_id": candidate.id,
                        "name": candidate.name,
                        "party": (
                            candidate.party.name if candidate.party else "Independent"
                        ),
                        "votes": candidate.votes,
                        "image_url": (
                            request.build_absolute_uri(candidate.image.url)
                            if candidate.image
                            else None
                        ),
                    }
                )

            positions_data.append(
                {
                    "position_id": position.id,
                    "position_title": position.title,
                    "candidates": candidates_data,
                }
            )

        return Response(
            {
                "election_id": election.id,
                "election_title": election.title,
                "positions": positions_data,
            }
        )
