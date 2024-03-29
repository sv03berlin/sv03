from json import loads
from clubapp.reservationflow.models import ReservationGroup
from typing import Any

from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.http import urlencode
from josepy.b64 import b64decode
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.db import transaction

from clubapp.club.models import User, Membership


class ClubOIDCAuthenticationBackend(OIDCAuthenticationBackend):  # type: ignore[misc]
    def get_userinfo(self, access_token: str, id_token: str, payload: str) -> Any:
        response = super().get_userinfo(access_token, id_token, payload)
        _, json, _ = access_token.split(".")
        payload_json = loads(b64decode(json).decode("utf-8"))  # type: dict[str, Any]
        response["group"] = payload_json.get("realm_access", {}).get("roles", [])
        return response

    def filter_users_by_claims(self, claims: dict[Any, Any]) -> "QuerySet[User]":
        if claims.get("username"):
            return User.objects.filter(username=claims["username"])
        if claims.get("email_verified"):
            return User.objects.filter(email=claims["email"])
        else:
            return User.objects.none()

    def verify_claims(self, claims: dict[Any, Any]) -> bool:
        scopes = self.get_settings("OIDC_RP_SCOPES", "openid email")
        if "email" in scopes.split() and "username" in scopes.split():
            return "email" in claims
        return True

    def get_username(self, claims: dict[Any, Any]) -> str:
        return claims.get("username", claims.get("email"))  # type: ignore[no-any-return]

    def get_membership(self, claims: dict[Any, Any]) -> Membership | None:
        return Membership.objects.filter(name=claims.get("membership")).first()

    def get_staff(self, claims: dict[Any, Any]) -> bool:
        return "staff" in claims.get("group", []) or self.get_superuser(claims)

    def get_superuser(self, claims: dict[Any, Any]) -> bool:
        return "admin" in claims.get("group", [])

    def member_permissions(self, claims: dict[Any, Any]) -> list[str]:
        return list(claims.get("member_permissions", "").strip().split(","))

    def grant_reservation_permissions(self, claims: dict[Any, Any], user: User) -> None:
        uc = self.member_permissions(claims)

        # add permissions to user
        for pm in list(ReservationGroup.objects.filter(internal_name__in=uc)):
            pm.users.add(user)
            pm.save()

        # remove permissions from user
        for pm in user.reservation_groups.all():
            if pm.internal_name not in uc:
                pm.users.remove(user)
                pm.save()

    @transaction.atomic
    def create_user(self, claims: dict[Any, Any]) -> User:
        user = User.objects.create_user(
            username=self.get_username(claims),
            email=claims["email"],
            first_name=claims.get("firstName", ""),
            last_name=claims.get("lastName", ""),
            is_staff=self.get_staff(claims),
            is_clubboat_user=claims.get("clubboat", False),
            is_boat_owner=claims.get("boat", False),
            is_superuser=self.get_superuser(claims),
            membership_type=self.get_membership(claims),
        )
        user.set_unusable_password()
        user.save()
        self.grant_reservation_permissions(claims, user)
        return user

    def update_user(self, user: User, claims: dict[Any, Any]) -> User:
        user.email = self.get_username(claims)
        user.first_name = claims.get("firstName", "")
        user.last_name = claims.get("lastName", "")
        user.is_staff = self.get_staff(claims)
        user.is_clubboat_user = claims.get("clubboat", False)
        user.is_boat_owner = claims.get("boat", False)
        user.is_superuser = self.get_superuser(claims)
        user.membership_type = self.get_membership(claims)
        user.save()
        self.grant_reservation_permissions(claims, user)

        if not user.is_active:
            raise User.DoesNotExist("User is inactive: {}".format(user.get_username()))

        return user


def provider_logout(request: "HttpRequest") -> "str":
    redirect_url = request.build_absolute_uri("/")
    return (
        settings.OIDC_OP_LOGOUT_ENDPOINT
        + "?"
        + urlencode({"post_logout_redirect_uri": redirect_url, "client_id": settings.OIDC_RP_CLIENT_ID})
    )


def provider_account_settings(request: "HttpRequest") -> "HttpResponseRedirect":
    kc_params = {"referrer": settings.THIS_APP_NAME, "referrer_uri": settings.VIRTUAL_HOST}
    url = request.build_absolute_uri(settings.KEYCLOAK_ACCOUNT_URL) + "?" + urlencode(kc_params)
    return HttpResponseRedirect(url)
