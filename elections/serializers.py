from rest_framework import serializers
from .models import PoliticalParty, Election, Candidate, Position
from votes.models import Vote


# ==============================
# POLITICAL PARTY SERIALIZER
# ==============================
class PoliticalPartySerializer(serializers.ModelSerializer):
    badge_url = serializers.SerializerMethodField()

    class Meta:
        model = PoliticalParty
        fields = ("id", "name", "abbreviation", "badge_url")

    def get_badge_url(self, obj):
        request = self.context.get("request")
        if obj.badge and request:
            return request.build_absolute_uri(obj.badge.url)
        return None


# ==============================
# CANDIDATE SERIALIZER (with vote count)
# ==============================
class CandidateSerializer(serializers.ModelSerializer):
    party = PoliticalPartySerializer(read_only=True)
    party_id = serializers.PrimaryKeyRelatedField(
        queryset=PoliticalParty.objects.all(),
        source="party",
        write_only=True,
        required=False,
    )

    image_url = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()  # NEW FIELD

    class Meta:
        model = Candidate
        fields = (
            "id",
            "name",
            "description",
            "image_url",
            "party",
            "party_id",
            "votes",  # include current vote count
        )

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_votes(self, obj):
        # Count votes for this candidate
        return obj.votes_received.count()


# ==============================
# POSITION SERIALIZER (with has_voted, can_vote, total_candidates, slug)
# ==============================
class PositionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    has_voted = serializers.SerializerMethodField()
    can_vote = serializers.SerializerMethodField()
    total_candidates = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Position
        fields = (
            "id",
            "title",
            "slug",
            "candidates",
            "has_voted",
            "can_vote",
            "total_candidates",
        )

    def get_has_voted(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Vote.objects.filter(voter=user, position=obj).exists()

    def get_can_vote(self, obj):
        request = self.context.get("request")
        user = request.user if request else None

        if not user or user.is_anonymous:
            return False  # anonymous users cannot vote

        # Can vote if election is active AND user hasn't voted for this position
        election_active = obj.election.is_active
        has_voted = Vote.objects.filter(voter=user, position=obj).exists()

        return election_active and not has_voted

    def get_total_candidates(self, obj):
        return obj.candidates.count()


# ==============================
# ELECTION SERIALIZER (with positions and slug)
# ==============================
class ElectionSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Election
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "start_date",
            "end_date",
            "is_active",
            "positions",
        )
