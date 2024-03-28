from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from clubapp.club.models import Ressort, User


class ClubWork(models.Model):
    ressort = models.ForeignKey(Ressort, on_delete=models.PROTECT, related_name="clubwork", verbose_name=_("Ressort"))

    title = models.CharField(max_length=127, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beschreibung"))

    date_time = models.DateTimeField(verbose_name=_("Datum und Uhrzeit"))
    max_duration = models.IntegerField(verbose_name=_("Maximale Dauer (in Minuten)"))
    max_participants = models.IntegerField(verbose_name=_("Maximale Teilnehmer:innenanzahl"))

    def __str__(self) -> str:
        return f"{self.title} am {self.date_time.strftime('%d.%m.%Y %H:%M')}"

    @cached_property
    def num_participants(self) -> int:
        return self.participations.count()

    @cached_property
    def registered_users(self) -> list[User]:
        return [p.user for p in self.participations.all()]

    @cached_property
    def mailto(self) -> str:
        return "mailto:" + ",".join([u.email for u in self.registered_users])


class ClubWorkParticipation(models.Model):
    title = models.CharField(max_length=127, verbose_name=_("Titel"))
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="clubwork_participations", verbose_name=_("Teilnehmer:in")
    )
    ressort = models.ForeignKey(
        Ressort, on_delete=models.PROTECT, related_name="clubwork_participations", verbose_name=_("Ressort")
    )
    clubwork = models.ForeignKey(
        ClubWork,
        on_delete=models.PROTECT,
        related_name="participations",
        null=True,
        verbose_name=_("Arbeitsdienst"),
        default=None,
        blank=True,
    )
    date_time = models.DateTimeField(verbose_name=_("Datum und Uhrzeit"))
    duration = models.IntegerField(verbose_name=_("Dauer (in Minuten)"))
    is_approved = models.BooleanField(verbose_name=_("Genehmigt"), default=False)
    approved_by = models.ForeignKey(
        User,
        related_name="approved_work",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Genehmigt von"),
        blank=True,
        default=None,
    )
    approve_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Genehmigt am"))
    description = models.TextField(verbose_name=_("Beschreibung"))

    def __str__(self) -> str:
        return f"{self.user} hilft bei {self.clubwork or self.title}"
