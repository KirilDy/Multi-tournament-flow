from django.contrib import admin
from .models import Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "created_by")
    list_filter = ("status",)
    search_fields = ("title",)