import subprocess
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ""
    help = "validating clubapp-dj openapi schema"
    requires_migrations_checks = False

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        cmd = "mypy . --config-file pyproject.toml"
        subprocess.run(cmd, shell=True, check=True)
