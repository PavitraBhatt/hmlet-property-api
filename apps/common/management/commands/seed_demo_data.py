"""Small demo dataset so the API can be poked at right after setup."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.contracts.services import create_contract
from apps.members.models import Member
from apps.properties.models import Property
from apps.units.models import Unit

DEMO_PASSWORD = "Sup3rSecret!"


class Command(BaseCommand):
    help = "Create a staff user, two properties with units, members and a few contracts."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        staff, created = User.objects.get_or_create(
            email="ops@hmlet.com", defaults={"full_name": "Ops Staff"}
        )
        if created:
            staff.set_password(DEMO_PASSWORD)
            staff.save(update_fields=["password"])

        somerset, _ = Property.objects.get_or_create(
            name="Cove Somerset", defaults={"address": "12 Somerset Road, Singapore 238164"}
        )
        tiong, _ = Property.objects.get_or_create(
            name="Hmlet Tiong Bahru", defaults={"address": "5 Kim Pong Road, Singapore 169178"}
        )

        units = {}
        for prop, number, rent in [
            (somerset, "04-12", "2500.00"),
            (somerset, "04-13", "2650.00"),
            (somerset, "10-01", "3800.00"),
            (tiong, "02-05", "2100.00"),
            (tiong, "02-06", "2100.00"),
        ]:
            unit, _ = Unit.objects.get_or_create(
                property=prop, unit_number=number, defaults={"monthly_rent": rent}
            )
            units[number] = unit

        members = {}
        for name, email in [
            ("Aditi Rao", "aditi.rao@example.com"),
            ("Marcus Tan", "marcus.tan@example.com"),
            ("Lena Fischer", "lena.fischer@example.com"),
        ]:
            member, _ = Member.objects.get_or_create(email=email, defaults={"full_name": name})
            members[email] = member

        today = date.today()
        day = timedelta(days=1)
        bookings = [
            # running right now
            ("aditi.rao@example.com", "04-12", today - 30 * day, today + 335 * day, None),
            # already finished
            ("marcus.tan@example.com", "02-05", today - 200 * day, today - 20 * day, None),
            # starts in a fortnight, at a negotiated rent
            ("lena.fischer@example.com", "10-01", today + 15 * day, today + 380 * day, "3600.00"),
        ]
        for email, unit_number, start, end, rent in bookings:
            unit = units[unit_number]
            if unit.contracts.exists():
                continue
            create_contract(
                member=members[email],
                unit_id=unit.pk,
                start_date=start,
                end_date=end,
                monthly_rent=rent,
                created_by=staff,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Seeded demo data. Login with ops@hmlet.com / {DEMO_PASSWORD}")
        )
