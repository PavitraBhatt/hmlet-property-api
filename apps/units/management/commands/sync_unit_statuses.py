from django.core.management.base import BaseCommand

from apps.units.models import Unit
from apps.units.services import sync_status


class Command(BaseCommand):
    help = "Recompute every unit's status from its contracts. Meant to run daily."

    def handle(self, *args, **options):
        changed = 0
        for unit in Unit.objects.prefetch_related("contracts"):
            before = unit.status
            sync_status(unit)
            if unit.status != before:
                changed += 1
                self.stdout.write(f"{unit} -> {unit.status}")

        self.stdout.write(self.style.SUCCESS(f"Done. {changed} unit(s) updated."))
