from django.conf import settings

from recipes.management.commands.load_base import LoadFromJsonCommand
from recipes.models import Ingredient


class Command(LoadFromJsonCommand):
    help = "Load ingredients from JSON file"
    model = Ingredient

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.set_defaults(
            path=str(settings.BASE_DIR / "data" / "ingredients.json")
        )
