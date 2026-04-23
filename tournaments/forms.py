# tournaments/forms.py
from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            'title',
            'description',
            'start_date',
            'registration_start',
            'registration_end',
            'max_teams'
        ]

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }