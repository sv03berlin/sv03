from json import loads
from typing import Any

from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.http import urlencode
from josepy.b64 import b64decode
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from clubapp.club.models import User


class ClubOIDCAuthenticationBackend(OIDCAuthenticationBackend):  # type: ignore[misc]
    def get_userinfo(self, access_token: str, id_token: str, payload: str) -> Any:
        response = super().get_userinfo(access_token, id_token, payload)
        _, json, _ = access_token.split(".")
        payload_json = loads(b64decode(json).decode("utf-8"))  # type: dict[str, Any]
        response["group"] = payload_json.get("realm_access", {}).get("roles", [])
        return response

    def filter_users_by_claims(self, claims: dict[Any, Any]) -> "QuerySet[User]":
        if claims.get("username"):  # this assumes that the username is the member number
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

    def create_user(self, claims: dict[Any, Any]) -> User:
        user = User.objects.create_user(
            username=claims["username"],
            email=claims["email"],
            first_name=claims.get("firstName", ""),
            last_name=claims.get("lastName", ""),
        )
        user.set_unusable_password()
        user.save()
        return user

    def update_user(self, user: User, claims: dict[Any, Any]) -> User:
        user.email = claims["email"]
        user.first_name = claims.get("firstName", "")
        user.last_name = claims.get("lastName", "")
        user.save()

        if not user.is_active:
            raise self.DoesNotExist("User is inactive: {}".format(user.get_username()))

        return user


def provider_logout(request: "HttpRequest") -> "str":
    kc_params = {"post_logout_redirect_uri": settings.OIDC_OP_LOGOUT_ENDPOINT, "client_id": settings.OIDC_RP_CLIENT_ID}
    return request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL) + "?" + urlencode(kc_params)
