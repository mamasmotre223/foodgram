from django.conf import settings

from recipes.management.commands.load_base import LoadFromJsonCommand
from recipes.models import Tag


class Command(LoadFromJsonCommand):
    help = "Load tags from JSON file"
    model = Tag
    default_path = str(settings.BASE_DIR / "data" / "tags.json")
