from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe


def short_link_redirect(request, recipe_id):
    if not Recipe.objects.filter(pk=recipe_id).exists():
        raise Http404
    return redirect(f"/recipes/{recipe_id}")
