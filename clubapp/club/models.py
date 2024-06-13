import logging

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


ARBEITDIENST_FREI_AB_ALTER = 67


class Membership(models.Model):
    name = models.CharField(max_length=63, unique=True, verbose_name=_("Mitgliedschaftsart"))
    internal_name = models.CharField(max_length=63, unique=True, verbose_name=_("Interner Name"))
    work_hours = models.IntegerField(verbose_name=_("Arbeitsstunden"))
    work_hours_boat_owner = models.IntegerField(verbose_name=_("Arbeitsstunden Bootseigner:in"))
    work_hours_club_boat_user = models.IntegerField(verbose_name=_("Arbeitsstunden Clubbootnutzer:in"))

    work_compensation = models.DecimalField(
        decimal_places=2, max_digits=5, verbose_name=_("Entschädigung pro Stunde in €")
    )

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    license = models.CharField(max_length=63, blank=True, verbose_name=_("Lizenznummer"))

    can_create_invoices = models.BooleanField(default=False, verbose_name=_("Nutzer darf Rechnungen erstellen"))
    is_boat_owner = models.BooleanField(default=False, verbose_name=_("Nutzer ist Bootseigner:in"))
    is_clubboat_user = models.BooleanField(default=False, verbose_name=_("Nutzer ist Clubbootnutzer:in"))
    birthday = models.DateField(verbose_name=_("Geburtstag"), default=None, null=True)

    openid_sub = models.UUIDField(blank=True, null=True, verbose_name=_("OpenID Sub"))

    member_id = models.CharField(max_length=32, blank=True, default="", verbose_name=_("Mitgliedsnummer"))

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @cached_property
    def membership_type(self) -> "MembershipYear|None":
        if (m := self.membership_years.filter(year=timezone.now().year).first()) is not None:
            return m
        return None

    @cached_property
    def membership(self) -> "str":
        if self.membership_type:
            return self.membership_type.membership_type.name
        return "Keine Mitgliedschaftsart hinterlegt"

    @cached_property
    def is_invoice_user(self) -> bool:
        return self.can_create_invoices or self.is_superuser

    @cached_property
    def is_ressort_user(self) -> bool:
        return Ressort.objects.filter(head__in=[self.pk]).exists() or self.is_superuser

    @cached_property
    def is_accountant_user(self) -> bool:
        return Ressort.objects.filter(head__in=[self.pk], is_accounting_ressort=True).exists() or self.is_superuser

    @cached_property
    def club_work_hours(self) -> int:
        return self.get_clubwork_year(timezone.now().year)

    def member_is_freed_from_work_by_age(self, year: int | None) -> bool:
        if year is None:
            year = timezone.now().year
        if self.birthday and year - self.birthday.year > ARBEITDIENST_FREI_AB_ALTER:
            return True
        return False

    def get_clubwork_year(self, year: int) -> int:
        work_hours = 0
        if self.member_is_freed_from_work_by_age(year):
            return 0
        membership_year = self.membership_years.filter(year=year).first()
        if membership_year:
            work_hours += membership_year.work_hours
            if self.is_boat_owner:
                work_hours += membership_year.work_hours_boat_owner
            if self.is_clubboat_user:
                work_hours += membership_year.work_hours_club_boat_user
        return work_hours

    @cached_property
    def hours_to_do(self) -> int:
        if self.membership_type:
            return self.club_work_hours
        return 0

    @cached_property
    def hours_done(self) -> float:
        return self.hours_done_year(timezone.now().year)

    @cached_property
    def hours_done_formatted(self) -> str:
        return self.get_time_formatted(self.hours_done)

    @cached_property
    def hours_to_do_formatted(self) -> str:
        return self.get_time_formatted(self.missing_hours(timezone.now().year))

    def get_time_formatted(self, time: float) -> str:
        return "{:02.0f}:{:02.0f}".format(*divmod(time * 60, 60))

    def hours_done_year(self, year: int) -> float:
        return (
            self.clubwork_participations.filter(date_time__year=year)
            .exclude(is_approved=False)
            .aggregate(models.Sum("duration"))
            .get("duration__sum")
            or 0
        ) / 60

    def club_work_compensation(self, year: int) -> float:
        if self.membership_type and not self.membership_type.full_work_compensation:
            return float(float(self.membership_type.work_compensation) * self.missing_hours(year))
        return 0

    def missing_hours(self, year: int) -> float:
        left = self.club_work_hours - self.hours_done_year(year)
        if left < 0:
            return 0
        return left

    @cached_property
    def unconfirmed_hours(self) -> float:
        return (
            self.clubwork_participations.filter(date_time__year=timezone.now().year)
            .filter(is_approved=False)
            .aggregate(models.Sum("duration"))
            .get("duration__sum")
            or 0
        )

    @cached_property
    def unconfirmed_hours_formatted(self) -> str:
        return self.get_time_formatted(self.unconfirmed_hours)

    def update_membership_year(self, membership_type: Membership) -> None:
        this_year = timezone.now().year
        membership_year = self.membership_years.filter(year=this_year).first()

        work_hours = membership_type.work_hours
        work_hours_boat_owner = membership_type.work_hours_boat_owner if self.is_boat_owner else 0
        work_hours_club_boat_user = membership_type.work_hours_club_boat_user if self.is_clubboat_user else 0

        if membership_year:
            membership_year.membership_type = membership_type
            membership_year.work_hours = work_hours
            membership_year.work_hours_boat_owner = work_hours_boat_owner
            membership_year.work_hours_club_boat_user = work_hours_club_boat_user
            membership_year.save()
        else:
            logger.info("Creating new membership year for %s in %s", self, this_year)
            MembershipYear.objects.create(
                user=self,
                year=this_year,
                membership_type=membership_type,
                work_hours=work_hours,
                work_hours_boat_owner=work_hours_boat_owner,
                work_hours_club_boat_user=work_hours_club_boat_user,
                work_compensation=membership_type.work_compensation,
            )


class MembershipYear(models.Model):
    year = models.IntegerField(verbose_name=_("Jahr"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membership_years", verbose_name=_("Nutzer"))
    membership_type = models.ForeignKey(Membership, on_delete=models.PROTECT, verbose_name=_("Mitgliedschaftsart"))

    work_hours = models.IntegerField(verbose_name=_("Arbeitsstunden (Überschreiben für ausgewähltes Jahr)"), default=0)
    work_hours_boat_owner = models.IntegerField(
        verbose_name=_("Arbeitsstunden Bootseigner:in (Überschreiben für ausgewähltes Jahr)"), default=0
    )
    work_hours_club_boat_user = models.IntegerField(
        verbose_name=_("Arbeitsstunden Clubbootnutzer:in (Überschreiben für ausgewähltes Jahr)"), default=0
    )
    work_compensation = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        verbose_name=_("Entschädigung pro Stunde in € (Überschreiben für ausgewähltes Jahr)"),
        default=0,
    )

    full_work_compensation = models.BooleanField(default=False, verbose_name=_("Vollständige Entschädigung erfolgt"))

    class Meta:
        unique_together = ("user", "year")
        verbose_name = "Membership in year"
        verbose_name_plural = "Memberships in years"

    def __str__(self) -> str:
        return f"{self.user} - {self.year} - {self.membership_type}"

    @cached_property
    def name(self) -> str:
        return self.membership_type.name


class Ressort(models.Model):
    name = models.CharField(max_length=63, unique=True, verbose_name=_("Ressortname"))
    internal_name = models.CharField(max_length=63, unique=True, verbose_name=_("Interner Ressortname"))
    head = models.ManyToManyField(User, related_name="ressort_head", verbose_name=_("Leiter:in"))
    is_accounting_ressort = models.BooleanField(default=False, verbose_name=_("Buchhaltungsressort"))

    def __str__(self) -> str:
        return self.name
