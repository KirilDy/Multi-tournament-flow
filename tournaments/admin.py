from django.contrib import admin
from .models import Tournament, Round, MustHaveCriteria


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "created_by")
    list_filter = ("status",)
    search_fields = ("title",)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("tournament", "order", "title", "status", "start_time", "end_time")
    list_filter = ("status", "tournament")
    search_fields = ("title", "description", "tech_requirements")
    ordering = ("tournament_id", "order")


@admin.register(MustHaveCriteria)
class MustHaveCriteriaAdmin(admin.ModelAdmin):
    list_display = ("round", "order", "text")
    list_filter = ("round__tournament", "round")
    search_fields = ("text",)
    ordering = ("round_id", "order")

