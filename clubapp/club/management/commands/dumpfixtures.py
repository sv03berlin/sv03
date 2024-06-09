from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.apps import apps
from pathlib import Path
from typing import Any

class Command(BaseCommand):
    help = "dumping fixtures for clubapp-dj"
    requires_migrations_checks = True

    path = Path("clubapp/club/fixtures/")

    def handle(self, *args: Any, **options: Any) -> None:
        """Dump fixtures for clubapp-dj. Excludes ManyToManyFields."""
        models = [apps.get_model('club', 'Ressort'), apps.get_model('club', 'Membership'), apps.get_model('reservationflow', 'ReservationGroup'), apps.get_model('reservationflow', 'ReservableThing')]

        for model in models:
            data = serialize('json', model.objects.all(), indent=4, use_natural_foreign_keys=True, use_natural_primary_keys=True, fields=[field.name for field in model._meta.fields])
            with open(self.path / f'{model.__name__}.json', 'w') as f:
                f.write(data)