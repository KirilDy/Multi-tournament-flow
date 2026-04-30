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
            # Перевірка чи турнір відкритий для реєстрації
            if not self.tournament.is_registration_open():
                raise ValidationError("Реєстрація на цей турнір закрита.")
            
            # Перевірка чи не досягнуто максимальну кількість команд
            if self.tournament.max_teams:
                current_teams = self.tournament.teams.count()
                if current_teams >= self.tournament.max_teams:
                    raise ValidationError("Досягнуто максимальну кількість команд.")
        return cleaned_data
    
    def save(self, commit=True):
        team = super().save(commit=False)
        if self.tournament:
            team.tournament = self.tournament
        if commit and self.instance:
            team.save()
        return team


class TeamMemberForm(forms.ModelForm):
    """Форма для додавання учасника в команду"""
    
    class Meta:
        model = TeamMember
        fields = ['full_name', 'email', 'is_captain']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ПІБ учасника'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'is_captain': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Зробити is_captain більш видимим
        self.fields['is_captain'].help_text = "Відзначте, якщо цей учасник є капітаном команди"


class TeamMemberFormSet(forms.BaseModelFormSet):
    """FormSet для додавання кількох учасників"""
    
    def clean(self):
        super().clean()
        # Перевірка чи є хоча б один учасник
        total_members = sum(1 for form in self.forms if form.has_changed() and not form.cleaned_data.get('DELETE', False))
        if total_members < 1:
            raise ValidationError("Потрібно додати хоча б одного учасник��.")
        
        # Перевірка чи є капітан
        has_captain = any(
            form.cleaned_data.get('is_captain', False) 
            for form in self.forms 
            if form.is_valid() and form.has_changed() and not form.cleaned_data.get('DELETE', False)
        )
        if not has_captain:
            raise ValidationError("У команді обов'язково має бути капітан.")


def get_team_member_formset(initial_data=None, extra=1):
    """Створює динамічний formset для учасників"""
    return forms.modelformset_factory(
        TeamMember,
        form=TeamMemberForm,
        formset=TeamMemberFormSet,
        extra=extra,
        fields=['full_name', 'email', 'is_captain'],
        widgets={
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ПІБ учасника'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'is_captain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    )
