from django import forms
from django.forms import inlineformset_factory

from .models import Tournament, Round, MustHaveCriteria, RoundSubmission


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


class RoundForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = [
            'title',
            'description',
            'tech_requirements',
            'start_time',
            'end_time',
            'status',
            'order',
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


MustHaveCriteriaFormSet = inlineformset_factory(
    Round,
    MustHaveCriteria,
    fields=['text', 'order'],
    extra=1,
    can_delete=True,
    widgets=None,
)


class RoundSubmissionForm(forms.ModelForm):
    class Meta:
        model = RoundSubmission
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

