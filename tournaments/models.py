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


class Round(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUBMISSION_CLOSED = "submission_closed", "Submission closed"
        EVALUATED = "evaluated", "Evaluated"

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="rounds",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_requirements = models.TextField()

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["tournament_id", "order"]
        unique_together = [("tournament", "order")]
        app_label = 'tournaments'

    def __str__(self):
        return f"{self.tournament.title} - Round {self.order}: {self.title}"


class MustHaveCriteria(models.Model):
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="must_have_criteria",
    )

    text = models.CharField(max_length=1024)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["round_id", "order"]
        unique_together = [("round", "order")]

    def __str__(self):
        return f"Round {self.round_id} criteria {self.order}"


class RoundSubmission(models.Model):
    """Здача капітаном команди для конкретного раунду."""

    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name="round_submissions",
    )

    captain_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="captain_submissions",
    )

    comment = models.TextField(blank=True, verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('round', 'team')]
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission round={self.round_id} team={self.team_id}"

