from django.contrib import admin
from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "candidate", "position", "timestamp")
    search_fields = ("voter__email", "candidate__name", "position__title")
    list_filter = ("position", "candidate")
    readonly_fields = ("voter", "candidate", "position", "timestamp")
