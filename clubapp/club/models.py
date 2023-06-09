from datetime import datetime
from functools import cached_property

from django.contrib.auth.models import AbstractUser
from django.db import models


class Membership(models.Model):
    name = models.CharField(max_length=63, unique=True)
    work_hours = models.IntegerField()
    work_hours_boat_owner = models.IntegerField()
    work_hours_club_boat_user = models.IntegerField()

    work_compensation = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    license = models.CharField(max_length=63, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    bic = models.CharField(max_length=63, blank=True)

    membership_type = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="users", null=True)
    can_create_invoices = models.BooleanField(default=False)
    is_boat_owner = models.BooleanField(default=False)
    is_clubboat_user = models.BooleanField(default=False)

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @cached_property
    def is_invoice_user(self) -> bool:
        return self.can_create_invoices or self.is_superuser

    @cached_property
    def is_resort_user(self) -> bool:
        return Resort.objects.filter(head=self).exists() or self.is_superuser

    @cached_property
    def is_accountant_user(self) -> bool:
        return Resort.objects.filter(head=self, is_accounting_resort=True).exists() or self.is_superuser

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
            self.approved_work.filter(clubwork__date_time__year=year)
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


class Resort(models.Model):
    name = models.CharField(max_length=63, unique=True)
    bank_account = models.CharField(max_length=255)
    head = models.ForeignKey(User, related_name="head", null=True, on_delete=models.SET_NULL)
    is_accounting_resort = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
