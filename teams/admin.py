from django.contrib import admin
from .models import Team, TeamMember

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0 # підказка для мінімум 2 учасників

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'city_school', 'registered_at')
    inlines = [TeamMemberInline]