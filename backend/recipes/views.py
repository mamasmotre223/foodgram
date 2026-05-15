from django.shortcuts import redirect
from rest_framework.generics import get_object_or_404

from recipes.models import Recipe


def short_link_redirect(request, recipe_id):
    get_object_or_404(Recipe.objects.only("id"), pk=recipe_id)
    return redirect(f"/recipes/{recipe_id}")
