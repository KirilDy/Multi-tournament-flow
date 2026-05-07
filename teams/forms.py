from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Team, TeamMember
from tournaments.models import Tournament


class TeamCreateForm(forms.ModelForm):
    """Форма для створення нової команди в турнірі"""

    class Meta:
        model = Team
        fields = ['name', 'city_school', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва команди'
            }),
            'city_school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Місто / Школа'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telegram / Discord'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.tournament:
            now = timezone.now()

            # Перевірка чи турнір доступний (не DRAFT, не FINISHED)
            if self.tournament.status in [Tournament.Status.DRAFT, Tournament.Status.FINISHED]:
                raise ValidationError("Реєстрація недоступна для цього турніру.")

            # СТОГА перевірка часу реєстрації
            if not (self.tournament.registration_start <= now <= self.tournament.registration_end):
                raise ValidationError(
                    "Реєстрація доступна тільки з {} по {} (Київський час)".format(
                        self.tournament.registration_start.strftime('%d.%m.%Y %H:%M'),
                        self.tournament.registration_end.strftime('%d.%m.%Y %H:%M'),
                    )
                )

            # Перевірка максимальної кількості команд
            if self.tournament.max_teams:
                current_teams = self.tournament.teams.count()
                if current_teams >= self.tournament.max_teams:
                    raise ValidationError("Досигнцутo максимаьну кількість команд для цього турніру.")

        return cleaned_data

    def save(self, commit=True):
        team = super().save(commit=False)
        if self.tournament:
            team.tournament = self.tournament
        if commit:
            team.save()
        return team


class TeamMemberForm(forms.ModelForm):
    """Форма для додавання учасника в команду (лише по email).

    full_name підтягуватися не потрібно — в коді ми його візьмемо з User.
    """

    class Meta:
        model = TeamMember
        fields = ['email', 'is_captain']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            }),
            'is_captain': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_captain'].help_text = 'Відзначте, якщo цей учасник є капітаном команди'


class TeamMemberFormSet(forms.BaseModelFormSet):
    """FormSet для додавання кількох учасників (не використовується в поточному UI)."""

    def clean(self):
        super().clean()
        total_members = sum(
            1
            for form in self.forms
            if form.has_changed() and not form.cleaned_data.get('DELETE', False)
        )
        if total_members < 1:
            raise ValidationError("Потрібно додати хоча б одного учасника.")

        has_captain = any(
            form.cleaned_data.get('is_captain', False)
            for form in self.forms
            if form.is_valid() and form.has_changed() and not form.cleaned_data.get('DELETE', False)
        )
        if not has_captain:
            raise ValidationError("У команді обов'язково має бути капітан.")


def get_team_member_formset(initial_data=None, extra=1):
    """Створює formset для TeamMember."""
    return forms.modelformset_factory(
        TeamMember,
        form=TeamMemberForm,
        formset=TeamMemberFormSet,
        extra=extra,
        fields=['email', 'is_captain'],
        widgets={
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'is_captain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    )

