from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Адміністратор"
        TEAM = "TEAM", "Команда"
        JURY = "JURY", "Журі"

    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        default=Role.TEAM
    )

    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
