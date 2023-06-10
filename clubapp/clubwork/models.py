from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from clubapp.club.models import Resort, User


class ClubWork(models.Model):
    resort = models.ForeignKey(Resort, on_delete=models.PROTECT, related_name="clubwork", verbose_name=_("Ressort"))

    title = models.CharField(max_length=127, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beschreibung"))

    date_time = models.DateTimeField(verbose_name=_("Datum und Uhrzeit"))
    max_duration = models.IntegerField(verbose_name=_("Maximale Dauer (in Minuten)"))
    max_participants = models.IntegerField(verbose_name=_("Maximale Teilnehmer:innenanzahl"))

    def __str__(self) -> str:
        return f"{self.title} ({self.date_time})"

    @cached_property
    def num_participants(self) -> int:
        return self.participations.count()

    @cached_property
    def registered_users(self) -> list[User]:
        return [p.user for p in self.participations.all()]


class ClubWorkParticipation(models.Model):
    title = models.CharField(max_length=127, verbose_name=_("Titel"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="clubwork_participations", verbose_name=_("Teilnehmer:in"))
    resort = models.ForeignKey(Resort, on_delete=models.PROTECT, related_name="clubwork_participations", verbose_name=_("Ressort"))
    clubwork = models.ForeignKey(
        ClubWork, on_delete=models.PROTECT, related_name="participations", null=True, verbose_name=_("Arbeitsdienst")
    )
    date_time = models.DateTimeField(verbose_name=_("Datum und Uhrzeit"))
    duration = models.IntegerField(verbose_name=_("Dauer (in Minuten)"))
    approved_by = models.ForeignKey(
        User, related_name="approved_work", on_delete=models.SET_NULL, null=True, verbose_name=_("Genehmigt von")
    )
    approve_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Genehmigt am"))
    description = models.TextField(verbose_name=_("Beschreibung"))
