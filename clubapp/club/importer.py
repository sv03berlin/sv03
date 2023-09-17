import xmltodict
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from clubapp.club.models import User, Membership
from django.core.mail import send_mail


def get_membership_type(membership_type: str) -> Membership | None:
    m = Membership.objects.filter(membership_id_for_import=membership_type)
    if m.exists():
        return m.first()
    return None


def get_username(symbol: str) -> str:
    candidate = symbol.split("@")[0]
    if not User.objects.filter(username=candidate).exists():
        return candidate

    nr = 1
    while True:
        candidate += str(nr)
        if not User.objects.filter(username=candidate).exists():
            return candidate
        nr += 1


def create_new_user(data: dict[str, str]) -> tuple[User, list[str]] | tuple[None, list[str]]:
    membership = get_membership_type(data["membership_type"])
    if not membership:
        return None, [f"Mitgliedschaftsart {data['membership_type']} nicht gefunden"]

    user = User.objects.create_user(
        username=data["username"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        membership_type=membership,
    )
    pw = User.objects.make_random_password()
    user.set_password(pw)
    user.save()
    try:
        send_mail(
            "Neue Anmeldedaten für {settings.VIRTUAL_HOST}",
            f"""
            Hallo {data["first_name"]} {data["last_name"]},

            du hast dich erfolgreich auf {settings.VIRTUAL_HOST} registriert.
            Deine Anmeldedaten lauten:

            Benutzername: {data["username"]}
            Passwort: {pw}
            Bitte ändere dein Passwort nach der ersten Anmeldung.

            Beste Grüße,
            {settings.VIRTUAL_HOST}
            """,
            settings.DEFAULT_FROM_EMAIL,
            [data["email"]],
        )
    except Exception:
        return user, [f"Benutzer:in {user} wurde erstellt, aber die E-Mail konnte nicht versendet werden."]
    return user, [f"Benutzer:in {user} wurde erstellt und die Anmeldedaten wurden per E-Mail versendet."]


def import_sewobe_xml(file: str | UploadedFile | list[object]) -> list[str]:
    return ["Not implemented yet!"]
