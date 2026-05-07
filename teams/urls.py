from django.urls import path
from .views import (
    TeamCreateView,
    TeamDetailView,
    TeamAddMemberView,
    TeamLeaveView,
    JuryTeamListView,
    JuryTournamentListView,
    TournamentTeamsView,
)


urlpatterns = [
    # Створення команди в турнірі
    path('tournament/<int:tournament_pk>/create/', TeamCreateView.as_view(), name='team_create'),
    
    # Перегляд деталей команди
    path('<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    
    # Додавання учасника в команду
    path('<int:pk>/add-member/', TeamAddMemberView.as_view(), name='team_add_member'),

    # Вихід учасника з команди
    path('<int:pk>/leave/', TeamLeaveView.as_view(), name='team_leave'),

    
    # Для журі: перегляд команд турніру
    path('tournament/<int:tournament_pk>/teams/', JuryTeamListView.as_view(), name='jury_team_list'),
    
    # Для журі: перегляд список турнірів
    path('jury/tournaments/', JuryTournamentListView.as_view(), name='jury_tournament_list'),
    
    # Перегляд команд турніру (для всіх учасників)
    path('tournament/<int:pk>/teams/', TournamentTeamsView.as_view(), name='tournament_teams'),
]
