from typing import Any
from django.core.management.base import BaseCommand
from clubapp.clubwork .models import ClubWork, ClubWorkParticipation
from django.db.transaction import atomic
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from logging import getLogger
from clubapp.club.models import User, Ressort
from django.conf import settings
from django.urls import reverse

logger = getLogger(__name__)

class Command(BaseCommand):
    help = "notify about upcoming clubwork"
    requires_migrations_checks = True

    @atomic
    def notify_ressort(self) -> None:
        users: set[User] = set()
        works: set[ClubWorkParticipation] = set()
        print(str(ClubWorkParticipation.objects.filter(is_approved=False, did_send_approve_hint=False)))
        for work in ClubWorkParticipation.objects.filter(is_approved=False, did_send_approve_hint=False):
            for head in work.ressort.head.all():
                users.add(head)
                works.add(work)

        for user in list(users):
            send_mail(
                subject=f"Gegehmigungen ausstehend für Arbeitsdienste",
                message=f"Hallo {user.first_name},\n\n"
                f"Es stehen noch Arbeitsdienste zur Genehmigung an.\n"
                f"Bitte überprüfe die Arbeitsdienste und genehmige diese.\n\n"
                f"Du kannst dich hier anmelden: {settings.VIRTUAL_HOST}{reverse('approve_clubwork_overview')}\n\n"
                f"Viele Grüße,\n"
                f"Der Vorstand",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

        
        for work in list(works):
            work.did_send_reminder = True
            work.save()


    def notify_member(self) -> None:
        for participation in ClubWorkParticipation.objects.filter(did_send_reminder=False, clubwork__date_time__lte=timezone.now() + timedelta(hours=24)):
            with atomic():
                user: User = participation.user
                try:
                    if participation.async_date:
                        msg = f"am {participation.date_time} ist der Arbeitsdienst {participation.title} fällig.\n"
                    else:
                        msg = f"es steht ein neuer Arbeitsdienst an {participation.title} am {participation.date_time}.\n"
                    send_mail(
                        subject=f"Arbeitsdienst {participation.title}",
                        message=f"Hallo {user.first_name},\n\n"
                        f"{msg}"
                        f"Beschreibung: {participation.description}\n\n"
                        f"Viele Grüße,\n"
                        f"Der Vorstand",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False
                    )
                    participation.did_send_reminder = True
                    participation.save()
                except Exception as e:
                    logger.exception(e)


    def handle(self, *args: Any, **options: Any) -> str | None:
        self.notify_ressort()
        self.notify_member()
        return None