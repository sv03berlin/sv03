from os import environ
from clubapp.club.models import User, Membership
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from django.db import transaction
from django.core.management.base import BaseCommand
from typing import Any
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

kc_username = environ.get("KC_USERNAME", "").strip()
kc_password = environ.get("KC_PASSWORD", "").strip()
kc_url = environ.get("KC_URL", "").strip()
kc_client_id = environ.get("KC_CLIENT_ID", "").strip()
kc_client_secret = environ.get("KC_CLIENT_SECRET", "").strip()
kc_realm = environ.get("KC_REALM", "").strip()

class Command(BaseCommand):
    requires_migrations_checks = False
    help = "KeyCloak Sync Job"

    def _get_users(self) -> Any:
        keycloak_connection = KeycloakOpenIDConnection(
            server_url=kc_url,
            username=kc_username,
            password=kc_password,
            verify=True,
            client_id=kc_client_id,
            client_secret_key=kc_client_secret,
            realm_name=kc_realm
        )

        keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

        return keycloak_admin.get_users()
    
    def get_user(self, oidc_sub: str, email: str, username: str) -> User | None:
        user = User.objects.filter(openid_sub=oidc_sub)
        if user.exists():
            return user.first()
        user = User.objects.filter(email=email)
        if user.exists():
            return user.first()
        user = User.objects.filter(username=username)
        if user.exists():
            return user.first()
        return User.objects.create(openid_sub=oidc_sub, email=email, username=username)

    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("Starting KeyCloak Sync Job")
        users = self._get_users()
        for kc_user in users:
            try:
                if "sewobe_parser" not in kc_user.get("managed_by", []):
                    logger.info("Ignoring non Sewobe Managed User")
                    continue

                with transaction.atomic():
                    db_user = self.get_user(kc_user["id"], kc_user["email"], kc_user["username"])
                    if db_user is None:
                        logger.error(f"Could not find user {kc_user.get('username')}")
                        continue
                    m_name = kc_user.get("attributes", {}).get("mitgliedschaft")
                    m = Membership.objects.filter(name__in=m_name).first()
                    if m is None:
                        logger.error("Could not find membership (%s) for user ", kc_user.get('username'), m_name)
                        continue

                    db_user.update_membership_year(m)

                    db_user.is_boat_owner = kc_user.get("attributes", {}).get("boat", "false") == "true"
                    db_user.is_clubboat_user = kc_user.get("attributes", {}).get("clubboat", "false") == "true"
            except Exception as e:
                logger.error(f"Error while syncing user ({kc_user.get('username')}): {e}")

