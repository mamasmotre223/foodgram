from collections import Counter

from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
    User,
)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (*DjoserUserSerializer.Meta.fields, "avatar", "is_subscribed")
        read_only_fields = fields

    def get_is_subscribed(self, author):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user,
                author=author,
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = fields


class IngredientAmountWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient",
    )
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source="recipe_ingredients",
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields

    def _is_recipe_related(self, recipe, model):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and model.objects.filter(user=request.user, recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        return self._is_recipe_related(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self._is_recipe_related(recipe, ShoppingCart)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(required=False)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def _validate_uniqueness(self, field_name, values, id_getter):
        ids = [id_getter(value) for value in values]
        duplicates = [item_id for item_id, count in Counter(ids).items() if count > 1]
        if duplicates:
            raise serializers.ValidationError(
                {
                    field_name: [
                        f"Повторяющиеся значения: {duplicates}"
                    ]
                }
            )

    def validate(self, attrs):
        if self.instance is None and "image" not in attrs:
            raise serializers.ValidationError(
                {"image": ["Обязательное поле."]}
            )

        ingredients = attrs.get("ingredients") or []
        tags = attrs.get("tags") or []
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": ["Добавьте продукты."]}
            )
        if not tags:
            raise serializers.ValidationError({"tags": ["Добавьте теги."]})

        self._validate_uniqueness(
            "ingredients",
            ingredients,
            lambda item: item["ingredient"].id,
        )
        self._validate_uniqueness("tags", tags, lambda tag: tag.id)
        return attrs

    def _save_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item["ingredient"],
                amount=item["amount"],
            )
            for item in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.set(validated_data.pop("tags"))
        instance.recipe_ingredients.all().delete()
        self._save_ingredients(instance, validated_data.pop("ingredients"))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class SubscriptionAuthorSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, "recipes", "recipes_count")

    def get_recipes(self, author):
        recipes = author.recipes.all()
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        if recipes_limit:
            try:
                recipes = recipes[: int(recipes_limit)]
            except ValueError:
                pass
        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data
