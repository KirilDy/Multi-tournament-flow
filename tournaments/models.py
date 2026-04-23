from django.db import models
from django.conf import settings


class Tournament(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        REGISTRATION = "REGISTRATION", "Registration"
        RUNNING = "RUNNING", "Running"
        FINISHED = "FINISHED", "Finished"

    title = models.CharField(max_length=255)
    description = models.TextField()

    start_date = models.DateField()

    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()

    max_teams = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tournaments'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_registration_open(self):
        from django.utils import timezone
        now = timezone.now()
        return self.registration_start <= now <= self.registration_end