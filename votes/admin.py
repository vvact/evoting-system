from django.contrib import admin
from .models import Vote

# 🔥 Admin Branding
admin.site.site_header = "E-Voting System Admin"
admin.site.site_title = "E-Voting Portal"
admin.site.index_title = "Welcome to the E-Voting Dashboard"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "candidate", "position", "timestamp")
    search_fields = ("voter__email", "candidate__name", "position__title")
    list_filter = ("position", "candidate")
    readonly_fields = ("voter", "candidate", "position", "timestamp")