import json
from pathlib import Path

from django.core.management.base import BaseCommand


class LoadFromJsonCommand(BaseCommand):
    model = None
    fixture_name = ""

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True)

    def handle(self, *args, **options):
        try:
            file_path = Path(options["path"])
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            created = len(
                self.model.objects.bulk_create(
                    (self.model(**item) for item in payload),
                    ignore_conflicts=True,
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Fixture {file_path.name}: created {created} records"
                )
            )
        except Exception as error:
            self.stderr.write(self.style.ERROR(f"Load failed: {error}"))
