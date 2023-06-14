from typing import Any, Callable, TypeVar, Union

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from clubapp.refundflow.models import User

F = TypeVar("F", bound=Callable[..., Any])


def is_super_user(view_func: F) -> F:
    """
    Decorator for views that checks that the user is admin
    """

    def check_user(user: Union[User, AbstractBaseUser, AnonymousUser]) -> bool:
        assert isinstance(user, User)
        return user.is_superuser

    return user_passes_test(check_user)(view_func)


def is_invoice_user(view_func: F) -> F:
    """
    Decorator for views that checks that the user is allowed to write invoices
    """

    def check_user(user: Union[User, AbstractBaseUser, AnonymousUser]) -> bool:
        assert isinstance(user, User)
        return user.is_invoice_user or user.is_superuser

    return user_passes_test(check_user)(view_func)


def is_ressort_user(view_func: F) -> F:
    """
    Decorator for views that checks that the user is ressort head or admin
    """

    def check_user(user: Union[User, AbstractBaseUser, AnonymousUser]) -> bool:
        assert isinstance(user, User)
        return user.is_ressort_user or user.is_superuser

    return user_passes_test(check_user)(view_func)


def is_accountant_user(view_func: F) -> F:
    """
    Decorator for views that checks that the user is accountant
    """

    def check_user(user: Union[User, AbstractBaseUser, AnonymousUser]) -> bool:
        assert isinstance(user, User)
        return user.is_accountant_user or user.is_superuser

    return user_passes_test(check_user)(view_func)
