from django.contrib import admin
from .models import PoliticalParty, Election, Candidate, Position
from django.utils.html import format_html


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "badge_preview")
    search_fields = ("name",)

    def badge_preview(self, obj):
        if obj.badge:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; border-radius:50%;" />',
                obj.badge.url,  # Cloudinary URL will work here
            )
        return "No Badge"

    badge_preview.short_description = "Badge"


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "is_active")
    search_fields = ("title",)
    list_filter = ("is_active",)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "position",
        "election",
        "party_badge_preview",
        "image_preview",
        "votes",
    )
    search_fields = ("name", "position__title", "election__title")
    list_filter = ("position", "party", "election")

    readonly_fields = ("votes",)

    def party_badge_preview(self, obj):
        if obj.party and obj.party.badge:
            return format_html(
                '<img src="{}" style="width:40px; height:40px; border-radius:50%;" />',
                obj.party.badge.url,  # Cloudinary URL works directly
            )
        return "Independent"

    party_badge_preview.short_description = "Party Badge"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; border-radius:50%;" />',
                obj.image.url,  # Cloudinary URL works directly
            )
        return "No Image"

    image_preview.short_description = "Candidate Photo"

    def save_model(self, request, obj, form, change):
        # Prevent votes from being updated manually
        if change:
            old_obj = Candidate.objects.get(pk=obj.pk)
            obj.votes = old_obj.votes

        # Prevent duplicate party candidate for the same position
        if obj.party:
            exists = (
                Candidate.objects.filter(position=obj.position, party=obj.party)
                .exclude(pk=obj.pk)
                .exists()
            )
            if exists:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    f"{obj.party.name} already has a candidate for the position {obj.position.title}."
                )

        super().save_model(request, obj, form, change)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "election")
    search_fields = ("title", "election__title")
    list_filter = ("election",)