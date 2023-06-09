import subprocess
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ""
    help = "does everyting needed before committing"
    requires_migrations_checks = False

    def handle(self, *args: Any, **options: Any) -> None:
        print("\033[1;32m" + "running formatter" + "\033[0m")
        cmd = "python3 manage.py format"
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
        print("\033[1;32m" + "running linter" + "\033[0m")
        cmd = "python3 manage.py lint"
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
        print("\033[1;32m" + "running type checker" + "\033[0m")
        cmd = "python3 manage.py typecheck"
        subprocess.run(cmd, shell=True, check=True)
