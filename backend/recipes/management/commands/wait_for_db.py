import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for the default database to be available."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        for _ in range(30):
            try:
                connections["default"].cursor()
                self.stdout.write(self.style.SUCCESS("Database available."))
                return
            except OperationalError:
                time.sleep(1)

        raise OperationalError("Database is unavailable after 30 seconds.")
