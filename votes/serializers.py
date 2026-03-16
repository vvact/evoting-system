from rest_framework import serializers
from .models import Vote


class VoteSerializer(serializers.ModelSerializer):
    position_title = serializers.CharField(source="position.title", read_only=True)
    candidate_name = serializers.CharField(source="candidate.name", read_only=True)
    candidate_party = serializers.CharField(
        source="candidate.party.name", default="Independent", read_only=True
    )

    class Meta:
        model = Vote
        fields = (
            "id",
            "voter",
            "position",
            "position_title",
            "candidate",
            "candidate_name",
            "candidate_party",
            "timestamp",
        )
        read_only_fields = ("voter", "timestamp")
