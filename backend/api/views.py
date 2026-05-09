from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeMinifiedSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingListExportSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription, User


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = User.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in {"subscriptions", "subscribe"}:
            return SubscriptionSerializer
        return UserSerializer

    def get_permissions(self):
        auth_actions = {"me", "set_password", "avatar", "subscriptions", "subscribe"}
        if self.action in auth_actions:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=("post",),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="set_password",
    )
    def set_password(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        if not current_password or not new_password:
            return Response(
                {
                    "new_password": ["Обязательное поле."],
                    "current_password": ["Обязательное поле."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Неверный пароль."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("post",),
        permission_classes=(permissions.AllowAny,),
        url_path="reset_password",
    )
    def reset_password(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"email": ["Обязательное поле."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not User.objects.filter(email=email).exists():
            return Response(
                {"email": ["Пользователь не найден."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("put", "delete"),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="me/avatar",
    )
    def avatar(self, request):
        user = request.user
        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=["avatar"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(
            user,
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        avatar_url = UserSerializer(
            user,
            context=self.get_serializer_context(),
        ).data["avatar"]
        return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user).order_by("id")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if request.method == "POST":
            if author == request.user:
                return Response(
                    {"errors": ["Нельзя подписаться на самого себя."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            _, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author,
            )
            if not created:
                return Response(
                    {"errors": ["Вы уже подписаны на этого автора."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).delete()
        if not deleted:
            return Response(
                {"errors": ["Подписка не найдена."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        return (
            Recipe.objects.select_related("author")
            .prefetch_related("tags", "recipe_ingredients__ingredient")
            .order_by("-created")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action in {"create", "partial_update"}:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def _relation_action(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            _, created = model.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response(
                    {"errors": ["Рецепт уже добавлен."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RecipeMinifiedSerializer(
                recipe,
                context=self.get_serializer_context(),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = model.objects.filter(user=request.user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {"errors": ["Рецепт не найден в списке."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        items = ShoppingListExportSerializer.aggregate_for_user(request.user)
        lines = ["Список покупок:", ""]
        for item in items:
            lines.append(
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}"
            )
        response = HttpResponse(
            "\n".join(lines),
            content_type="text/plain; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="shopping-list.txt"'
        return response

    @action(detail=True, methods=("get",), url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f"/s/{format(recipe.id, 'x')}/")
        return Response({"short-link": short_link})


class ShortLinkRedirectView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, code):
        try:
            recipe_id = int(code, 16)
        except ValueError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f"/recipes/{recipe_id}")

