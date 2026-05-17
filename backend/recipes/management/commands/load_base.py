import json
from pathlib import Path

from django.core.management.base import BaseCommand


class LoadFromJsonCommand(BaseCommand):
    model = None
    default_path = None

    def add_arguments(self, parser):
        parser.add_argument("--path", default=self.default_path)

    def handle(self, *args, **options):
        try:
            file_path = Path(options["path"])
            old_count = self.model.objects.count()
            self.model.objects.bulk_create(
                (
                    self.model(**item)
                    for item in json.loads(
                        file_path.read_text(encoding="utf-8")
                    )
                ),
                ignore_conflicts=True,
            )
            created = self.model.objects.count() - old_count
            self.stdout.write(
                self.style.SUCCESS(
                    f"Фикстура {file_path.name}: создано {created} записей"
                )
            )
        except Exception as error:
            self.stderr.write(self.style.ERROR(f"Ошибка загрузки: {error}"))
