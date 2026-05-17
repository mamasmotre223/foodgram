from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

MIN_RECIPE_VALUE = 1


class Tag(models.Model):
    name = models.CharField("Название", max_length=32, unique=True)
    slug = models.SlugField("Идентификатор", max_length=32, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=128)
    measurement_unit = models.CharField("Единица измерения", max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_name_measurement_unit",
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField("Название", max_length=256)
    image = models.ImageField("Изображение", upload_to="recipes/images/")
    text = models.TextField("Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Продукты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления",
        validators=[MinValueValidator(MIN_RECIPE_VALUE)],
    )

    class Meta:
        ordering = ("-created",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Продукт",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_RECIPE_VALUE)],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Продукт в рецепте"
        verbose_name_plural = "Продукты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.ingredient} -> {self.recipe}"


class RecipeRelation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="%(class)s_unique_user_recipe",
            )
        ]


class Favorite(RecipeRelation):
    class Meta(RecipeRelation.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(RecipeRelation):
    class Meta(RecipeRelation.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
