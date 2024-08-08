import sys
from typing import Any

from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        sys.argv = ["manage.py", "runserver", "127.0.0.1:8000"]
        execute_from_command_line(sys.argv)
