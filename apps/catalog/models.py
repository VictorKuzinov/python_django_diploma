from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Category(models.Model):
    """
    Модель категории каталога товаров.

    Категории могут образовывать древовидную структуру:
    - родительская категория
    - дочерние категории (subcategories)

    Используется для группировки товаров в каталоге Megano.
    """

    title = models.CharField(
        max_length=100,
        verbose_name="Название категории"
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="Родительская категория"
    )

    image = models.ImageField(
        upload_to="category/",
        verbose_name="Файл изображения"
    )

    image_alt = models.CharField(
        max_length=128,
        verbose_name="Описание изображения"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активная категория"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        """
        Строковое представление категории.
        """
        return self.title


class Product(models.Model):
    """
    Модель товара каталога.

    Содержит основную информацию о товаре:
    - название
    - описание
    - цену
    - количество на складе
    - рейтинг и количество отзывов

    Товар относится к одной категории и может иметь:
    - несколько изображений
    - несколько тегов.
    """

    category = models.ForeignKey(
        "Category",
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name="Категория товара"
    )

    price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена товара"
    )

    count = models.IntegerField(
        default=0,
        verbose_name="Количество товара"
    )

    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время добавления товара"
    )

    title = models.CharField(
        max_length=100,
        verbose_name="Название товара"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание товара"
    )

    free_delivery = models.BooleanField(
        default=False,
        verbose_name="Бесплатная доставка"
    )

    tags = models.ManyToManyField(
        "Tag",
        related_name="products",
        verbose_name="Теги"
    )

    reviews = models.IntegerField(
        default=0,
        verbose_name="Количество отзывов"
    )

    rating = models.DecimalField(
        default=0,
        max_digits=3,
        decimal_places=2,
        verbose_name="Рейтинг товара",
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        """
        Строковое представление товара.
        """
        return self.title


class ProductImage(models.Model):
    """
    Модель изображения товара.

    Один товар может иметь несколько изображений.
    Используется для отображения галереи товара в каталоге.
    """

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар"
    )

    src = models.ImageField(
        upload_to="product/",
        verbose_name="Файл изображения товара"
    )

    alt = models.CharField(
        max_length=128,
        verbose_name="Описание изображения"
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Изображение товара: {self.product.title}"


class Tag(models.Model):
    """
    Модель тега товара.

    Теги используются для фильтрации и группировки товаров
    в каталоге (например: Gaming, SSD, Laptop и т.п.).
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название тега"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        """
        Строковое представление тега.
        """
        return self.name
