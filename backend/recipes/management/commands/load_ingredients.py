import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(settings.BASE_DIR / "data" / "ingredients.json"),
        )

    def handle(self, *args, **options):
        file_path = Path(options["path"])
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        with file_path.open("r", encoding="utf-8") as file:
            ingredients = json.load(file)
        objects = []
        for ingredient in ingredients:
            objects.append(
                Ingredient(
                    name=ingredient["name"],
                    measurement_unit=ingredient["measurement_unit"],
                )
            )
        Ingredient.objects.bulk_create(objects, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(objects)} ingredients")
        )
