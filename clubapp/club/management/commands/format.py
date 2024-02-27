import subprocess  # nosec
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "formating clubapp-dj"
    requires_migrations_checks = False

    def handle(self, *args: Any, **options: Any) -> None:
        subprocess.run(["ruff", "format", "."], check=True)  # nosec
