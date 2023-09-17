# import xmltodict
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import send_mail

from clubapp.club.models import Membership, User


def get_membership_type(membership_type: str) -> Membership | None:
    m = Membership.objects.filter(membership_id_for_import=membership_type)
    if m.exists():
        return m.first()
    return None


def get_username(candidate: str) -> str:
    if not User.objects.filter(username=candidate).exists():
        return candidate

    nr = 1
    while True:
        candidate += str(nr)
        if not User.objects.filter(username=candidate).exists():
            return candidate
        nr += 1


def send_new_password(user: User) -> tuple[User, list[str]]:
    pw = User.objects.make_random_password()
    user.set_password(pw)
    user.save()
    try:
        send_mail(
            "Neue Anmeldedaten für {settings.VIRTUAL_HOST}",
            f"""
            Hallo {user.first_name} {user.last_name},

            Deine Anmeldedaten lauten:

            Benutzername: {user.username}
            Passwort: {pw}
            Bitte ändere dein Passwort nach der nächsten Anmeldung.

            Beste Grüße,
            {settings.VIRTUAL_HOST}
            """,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
    except Exception:
        return user, [f"Benutzer:in {user} wurde erstellt, aber die E-Mail konnte nicht versendet werden."]
    return user, []


def create_new_user(data: dict[str, str]) -> tuple[User, list[str]] | tuple[None, list[str]]:
    membership = get_membership_type(data["membership_type"])
    if not membership:
        return None, [f"Mitgliedschaftsart {data['membership_type']} nicht gefunden"]

    user = User.objects.create_user(
        username=get_username(f"{data['first_name']}.{data['last_name']}"),
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        membership_type=membership,
        membership_id=data["membership_id"],
    )
    return send_new_password(user)


def import_sewobe_xml(file: str | UploadedFile | list[object]) -> list[str]:
    return ["Not implemented yet!"]
