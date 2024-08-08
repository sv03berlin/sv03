import os
import subprocess
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ""
    help = "linting clubapp-dj"
    requires_migrations_checks = False

    def handle(self, *args: Any, **options: Any) -> None:
        cmd = "ruff check . --fix"
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
