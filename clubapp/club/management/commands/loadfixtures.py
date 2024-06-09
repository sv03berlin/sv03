from django.core.management import call_command
from pathlib import Path
from typing import Any
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "load fixtures for clubapp-dj"
    requires_migrations_checks = True

    path = Path("clubapp/club/fixtures/")

    files_to_load = ["Ressort", "Membership", "ReservationGroup", "ReservableThing"] # order matters because of foreign keys

    def handle(self, *args: Any, **options: Any) -> str | None:
        """Load fixtures for clubapp-dj."""
        for file in self.files_to_load:
            call_command("loaddata", self.path / f"{file}.json")
            print(f"Loaded {file}.json\n---")
        return "Successfully loaded fixtures"