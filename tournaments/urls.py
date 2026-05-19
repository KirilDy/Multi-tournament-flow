from django.urls import path
from .views import *

urlpatterns = [
    path('list/', TournamentListView.as_view(), name='tournament_list'),
    path('create/', TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/edit/', TournamentEditView.as_view(), name='tournament_edit'),
    path('<int:pk>/change-status/', TournamentChangeStatusView.as_view(), name='tournament_change_status'),
    path('<int:pk>/delete/', TournamentDeleteView.as_view(), name='tournament_delete'),

    # Rounds
    path('tournament/<int:tournament_pk>/round/create/', RoundCreateView.as_view(), name='round_create'),
    path('tournament/<int:tournament_pk>/round/<int:pk>/edit/', RoundEditView.as_view(), name='round_edit'),
    path('tournament/<int:tournament_pk>/round/<int:pk>/', RoundDetailView.as_view(), name='round_detail'),
    path('tournament/<int:tournament_pk>/round/<int:pk>/submit/', RoundSubmissionCreateView.as_view(), name='round_submit'),
]

