from django.db import models
from django.conf import settings
from elections.models import Candidate, Position


class Vote(models.Model):
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name="votes_received"
    )
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="votes_received"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("voter", "position")

    def __str__(self):
        return f"{self.voter.email} voted for {self.candidate.name} in {self.position.title}"
