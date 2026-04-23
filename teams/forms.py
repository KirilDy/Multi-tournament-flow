from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_team_registration(team):
    # Налаштування дат (можна винести в БД або settings)
    REGISTRATION_START = timezone.datetime(2026, 4, 1, tzinfo=timezone.utc)
    REGISTRATION_END = timezone.datetime(2026, 5, 1, tzinfo=timezone.utc)
    now = timezone.now()

    # Перевірка періоду
    if not (REGISTRATION_START <= now <= REGISTRATION_END):
        raise ValidationError("Реєстрація наразі закрита.")

    # Перевірка кількості учасників (викликати перед фіналізацією реєстрації)
    members_count = team.members.count()
    if members_count < 2:
        raise ValidationError("У команді має бути мінімум 2 учасники.")
    
    if not team.members.filter(is_captain=True).exists():
        raise ValidationError("У команді обов'язково має бути капітан.")