from django.urls import path
from .views import *

urlpatterns = [
    path('', TournamentListView.as_view(), name='tournament_list'),
    path('create/', TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/edit/', TournamentEditView.as_view(), name='tournament_edit'),
    path('<int:pk>/change-status/', TournamentChangeStatusView.as_view(), name='tournament_change_status'),
    path('<int:pk>/delete/', TournamentDeleteView.as_view(), name='tournament_delete'),
]