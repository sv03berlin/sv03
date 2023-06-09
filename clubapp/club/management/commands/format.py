import subprocess  # nosec
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "formating clubapp-dj"
    requires_migrations_checks = False

    def handle(self, *args: Any, **options: Any) -> None:
        subprocess.run(["isort", "."], check=True)  # nosec
        subprocess.run(["black", ".", "--config", "/code/pyproject.toml"], check=True)  # nosec
