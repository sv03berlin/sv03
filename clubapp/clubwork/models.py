from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from clubapp.club.models import Ressort, User
from clubapp.clubapp.utils import AuthenticatedHttpRequest

logger = getLogger(__name__)


class ClubWork(models.Model):
    ressort = models.ForeignKey(Ressort, on_delete=models.PROTECT, related_name="clubwork", verbose_name=_("Ressort"))

    title = models.CharField(max_length=127, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beschreibung"))

    date_time = models.DateTimeField(verbose_name=_("Datum und Uhrzeit"))
    async_date = models.BooleanField(
        verbose_name=_("Eigenständige Abarbeitung mit Terminplanung. Das Datum ist als Frist zu interpretieren."),
        default=False,
    )
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

    @cached_property
    def is_full(self) -> bool:
        return self.max_participants == self.num_participants


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

    did_send_reminder = models.BooleanField(default=False)
    did_send_approve_hint = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user} hilft bei {self.clubwork or self.title}"

    @property
    def async_date(self) -> bool:
        if self.clubwork:
            return self.clubwork.async_date
        return False

    def notify_approval(self, request: AuthenticatedHttpRequest) -> None:
        try:
            send_mail(
                subject=f"Arbeitsdienst '{self.title}' wurde genehmigt",
                message=f"Hallo {self.user.first_name},\n\n"
                f"Dein Arbeitsdienst '{self.title}' vom {self.date_time} wurde genehmigt.\n\n"
                f"Viele Grüße,\n"
                f"{request.user.first_name} {request.user.last_name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001
            logger.warning("Email to %s not successful", self.user.email)
            messages.error(request, f"Email an {self.user.email} fehlgeschlagen.")
