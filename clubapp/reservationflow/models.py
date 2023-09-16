from django.db import models
from django.utils.translation import gettext_lazy as _

from clubapp.club.models import User

class ReservationGroup(models.Model):
    class Meta:
        verbose_name = _("Reservierungsgruppe")
        verbose_name_plural = _("Reservierungsgruppen")

    name = models.CharField(max_length=100)
    description = models.TextField()

    users = models.ManyToManyField(
        User,
        related_name="reservation_groups",
        verbose_name=_("Benutzer:innen in Reservierungsgruppe")
    )

    def __str__(self) -> str:
        return self.name


class ReservabelThing(models.Model):
    class Meta:
        verbose_name = _("Reservierbares Objekt")
        verbose_name_plural = _("Reservierbare Objekte")

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Beschreibung"))
    reservation_group = models.ForeignKey(ReservationGroup, on_delete=models.CASCADE, verbose_name="Reservierungsgruppe")
    all_can_reserve = models.BooleanField(default=False, verbose_name=_("Reservierbar von allen"))

    def __str__(self) -> str:
        return self.name


class Reservation(models.Model):
    class Meta:
        verbose_name = _("Reservierung")
        verbose_name_plural = _("Reservierungen")

    thing = models.ForeignKey(ReservabelThing, on_delete=models.CASCADE, verbose_name=_("Reservierungsobjekt"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Benutzer:in"))
    start = models.DateTimeField(verbose_name=_("Beginn der Reservierung"))
    end = models.DateTimeField(verbose_name=_("Ende der Reservierung"))

    def __str__(self) -> str:
        return f"{self.thing.name} {self.start} {self.end} - {self.user}"
