from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeMinifiedSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SubscriptionAuthorSerializer,
    TagSerializer,
    UserSerializer,
)
from api.shopping_list import build_shopping_list_text
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=("put", "delete"),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="me/avatar",
    )
    def avatar(self, request):
        if request.method == "DELETE":
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save(update_fields=["avatar"])
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "avatar": UserSerializer(
                    request.user,
                    context=self.get_serializer_context(),
                ).data["avatar"]
            }
        )

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscriptionAuthorSerializer(
                self.paginate_queryset(
                    self.get_queryset().filter(author_subscriptions__user=request.user)
                ),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        if request.method == "DELETE":
            get_object_or_404(
                Subscription,
                user=request.user,
                author_id=pk,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = self.get_object()
        if author == request.user:
            raise serializers.ValidationError(
                {"errors": ["Нельзя подписаться на самого себя."]}
            )

        _, created = Subscription.objects.get_or_create(
            user=request.user,
            author=author,
        )
        if not created:
            raise serializers.ValidationError(
                {"errors": [f"Вы уже подписаны на {author.username}."]}
            )
        return Response(
            SubscriptionAuthorSerializer(author, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.select_related("author")
        .prefetch_related("tags", "recipe_ingredients__ingredient")
        .distinct()
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in {"create", "partial_update"}:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _relation_action(self, request, pk, model):
        if request.method == "DELETE":
            get_object_or_404(
                model,
                user=request.user,
                recipe_id=pk,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )
        if not created:
            raise serializers.ValidationError(
                {
                    "errors": [
                        f"Рецепт '{recipe.name}' уже добавлен в "
                        f"{model._meta.verbose_name}."
                    ]
                }
            )
        return Response(
            RecipeMinifiedSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self._relation_action(request, pk, Favorite)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="shopping_cart",
    )
    def shopping_cart(self, request, pk=None):
        return self._relation_action(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        return FileResponse(
            build_shopping_list_text(request.user),
            as_attachment=True,
            filename="shopping-list.txt",
            content_type="text/plain",
        )

    @action(detail=True, methods=("get",), url_path="get-link")
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise NotFound(detail=f"Рецепт с id={pk} не найден.")
        return Response(
            {
                "short-link": request.build_absolute_uri(
                    reverse("short-link", args=[pk])
                )
            }
        )
