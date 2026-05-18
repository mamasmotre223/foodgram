from django.conf import settings

from recipes.management.commands.load_base import LoadFromJsonCommand
from recipes.models import Ingredient


class Command(LoadFromJsonCommand):
    help = "Load ingredients from JSON file"
    model = Ingredient
    default_path = settings.BASE_DIR / "data" / "ingredients.json"
