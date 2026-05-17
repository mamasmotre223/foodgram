import time

from django.core.management.base import BaseCommand
from django.db import OperationalError, connections


class Command(BaseCommand):
    help = "Wait until the default database accepts connections."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        connection = connections["default"]
        for _ in range(30):
            try:
                connection.ensure_connection()
            except OperationalError:
                time.sleep(1)
            else:
                self.stdout.write(self.style.SUCCESS("Database is available."))
                return
        raise OperationalError("Database is not available after 30 seconds.")
