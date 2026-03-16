from django.db import models
from django.utils.text import slugify


# -------------------------
# Political Party Model
# -------------------------
class PoliticalParty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=10, blank=True)
    badge = models.ImageField(upload_to="party_badges/", blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Political Parties"

    def __str__(self):
        return self.name


# -------------------------
# Election Model
# -------------------------
class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure unique slug
            while Election.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# -------------------------
# Position Model
# -------------------------
class Position(models.Model):
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name="positions"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure unique slug
            while Position.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.election.title})"


# -------------------------
# Candidate Model
# -------------------------
class Candidate(models.Model):
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name="candidates"
    )
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name="candidates"
    )
    name = models.CharField(max_length=255)
    party = models.ForeignKey(
        PoliticalParty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidates",
    )
    description = models.TextField(blank=True)
    votes = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="candidate_images/", blank=True, null=True)

    class Meta:
        unique_together = (
            ("party", "position"),  # ✅ Only one candidate per party per position
        )

    def __str__(self):
        party_name = self.party.name if self.party else "Independent"
        return f"{self.name} ({party_name}) for {self.position.title}"
