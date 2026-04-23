from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва команди")
    city_school = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Місто / школа"
    )
    contact = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Telegram / Discord"
    )
    registered_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата реєстрації"
    )

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_memberships")
    full_name = models.CharField(max_length=255, verbose_name="ПІБ учасника")
    email = models.EmailField(verbose_name="Email")
    is_captain = models.BooleanField(default=False, verbose_name="Капітан")

    class Meta:
        # Валідація: Email унікальні в межах однієї команди
        unique_together = ('team', 'email')
        verbose_name = "Учасник команди"
        verbose_name_plural = "Учасники команд"

    def clean(self):
        # 1. Один капітан на команду
        if self.is_captain:
            qs = TeamMember.objects.filter(team=self.team, is_captain=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("У команди вже є капітан.")

        # 2. Не можна зареєструватись двічі одним і тим самим email капітана в межах турніру
        # (якщо цей учасник мітить у капітани)
        if self.is_captain:
            if TeamMember.objects.filter(email=self.email, is_captain=True).exclude(pk=self.pk).exists():
                raise ValidationError("Цей email вже зареєстрований як капітан в іншій команді.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)