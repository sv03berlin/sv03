from collections.abc import Callable
from typing import Any, TypeVar

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from clubapp.refundflow.models import User

F = TypeVar("F", bound=Callable[..., Any])


def is_super_user[F: Callable[..., Any]](view_func: F) -> F:
    """Decorator for views that checks that the user is admin."""

    def check_user(user: User | AbstractBaseUser | AnonymousUser) -> bool:
        assert isinstance(user, User)  # noqa: S101
        return user.is_superuser

    return user_passes_test(check_user)(view_func)


def is_invoice_user[F: Callable[..., Any]](view_func: F) -> F:
    """Decorator for views that checks that the user is allowed to write invoices."""

    def check_user(user: User | AbstractBaseUser | AnonymousUser) -> bool:
        assert isinstance(user, User)  # noqa: S101
        return user.is_invoice_user or user.is_superuser

    return user_passes_test(check_user)(view_func)


def is_ressort_user[F: Callable[..., Any]](view_func: F) -> F:
    """Decorator for views that checks that the user is ressort head or admin."""

    def check_user(user: User | AbstractBaseUser | AnonymousUser) -> bool:
        assert isinstance(user, User)  # noqa: S101
        return user.is_ressort_user or user.is_superuser

    return user_passes_test(check_user)(view_func)


def is_accountant_user[F: Callable[..., Any]](view_func: F) -> F:
    """Decorator for views that checks that the user is accountant."""

    def check_user(user: User | AbstractBaseUser | AnonymousUser) -> bool:
        assert isinstance(user, User)  # noqa: S101
        return user.is_accountant_user or user.is_superuser

    return user_passes_test(check_user)(view_func)
