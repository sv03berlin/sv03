from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class Membership(models.Model):
    name = models.CharField(max_length=63, unique=True, verbose_name=_("Mitgliedschaftsart"))
    work_hours = models.IntegerField(verbose_name=_("Arbeitsstunden"))
    work_hours_boat_owner = models.IntegerField(verbose_name=_("Arbeitsstunden Bootseigner:in"))
    work_hours_club_boat_user = models.IntegerField(verbose_name=_("Arbeitsstunden Clubbootnutzer:in"))

    work_compensation = models.DecimalField(decimal_places=2, max_digits=5, verbose_name=_("Entschädigung pro Stunde in €"))

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    license = models.CharField(max_length=63, blank=True, null=True, verbose_name=_("Lizenznummer"))

    membership_type = models.ForeignKey(
        Membership, on_delete=models.PROTECT, related_name="users", null=True, verbose_name=_("Mitgliedschaftsart")
    )
    can_create_invoices = models.BooleanField(default=False, verbose_name=_("Nutzer darf Rechnungen erstellen"))
    is_boat_owner = models.BooleanField(default=False, verbose_name=_("Nutzer ist Bootseigner:in"))
    is_clubboat_user = models.BooleanField(default=False, verbose_name=_("Nutzer ist Clubbootnutzer:in"))

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @cached_property
    def is_invoice_user(self) -> bool:
        return self.can_create_invoices or self.is_superuser

    @cached_property
    def is_ressort_user(self) -> bool:
        return Ressort.objects.filter(head=self).exists() or self.is_superuser

    @cached_property
    def is_accountant_user(self) -> bool:
        return Ressort.objects.filter(head=self, is_accounting_ressort=True).exists() or self.is_superuser

    @cached_property
    def club_work_hours(self) -> int:
        if self.membership_type:
            work_hours = self.membership_type.work_hours
            if self.is_boat_owner:
                work_hours = self.membership_type.work_hours_boat_owner
            if self.is_clubboat_user:
                work_hours = self.membership_type.work_hours_club_boat_user
            return work_hours
        return 0

    @cached_property
    def hours_to_do(self) -> int:
        if self.membership_type:
            return self.club_work_hours
        return 0

    @cached_property
    def hours_done(self) -> int:
        return self.hours_done_year(datetime.now().year)

    def hours_done_year(self, year: int) -> int:
        return (
            self.clubwork_participations.filter(date_time__year=year)
            .exclude(approved_by=None)
            .aggregate(models.Sum("duration"))
            .get("duration__sum")
            or 0
        )

    def club_work_compensation(self, year: int) -> float:
        if self.membership_type:
            return float(self.membership_type.work_compensation * self.missing_hours(year))
        return 0

    def missing_hours(self, year: int) -> int:
        return self.club_work_hours - self.hours_done_year(year)


class Ressort(models.Model):
    name = models.CharField(max_length=63, unique=True, verbose_name=_("Ressortname"))
    bank_account = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Buchungskonto"))
    head = models.ForeignKey(User, related_name="head", null=True, on_delete=models.SET_NULL, verbose_name=_("Vorstehende:r"))
    is_accounting_ressort = models.BooleanField(default=False, verbose_name=_("Buchhaltungsressort"))

    def __str__(self) -> str:
        return self.name
