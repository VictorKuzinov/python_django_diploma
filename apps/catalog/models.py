from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    Модель категории каталога товаров.

    Поддерживает древовидную структуру:
    - родительская категория (parent)
    - дочерние категории (children)

    Особенности:
    - используется для построения каталога
    - поддерживает вложенность категорий

    Поля:
    - is_active — позволяет скрывать категории без удаления
    - image / image_alt — используются на фронтенде

    Используется для:
    - фильтрации товаров
    - навигации по каталогу
    """

    title = models.CharField(max_length=100, verbose_name="Название категории")

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="Родительская категория",
    )

    image = models.ImageField(upload_to="category/", verbose_name="Файл изображения")

    image_alt = models.CharField(max_length=128, verbose_name="Описание изображения")

    is_active = models.BooleanField(default=True, verbose_name="Активная категория")

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
    - название, описание, цена
    - количество на складе (count)
    - рейтинг и количество отзывов (reviews, rating)

    Особенности:
    - поддерживает soft-delete через поле is_deleted
    - рейтинг и количество отзывов обновляются автоматически через signals
    - связан с категорией (Category)
    - может иметь несколько изображений (ProductImage)
    - может иметь несколько тегов (Tag)
    - может участвовать в акциях (Sale)

    Используется в:
    - каталоге товаров
    - корзине (Basket)
    - заказах (Order)
    """

    category = models.ForeignKey(
        "Category",
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name="Категория товара",
    )

    price = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, verbose_name="Цена товара"
    )

    count = models.IntegerField(default=0, verbose_name="Количество товара")

    date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время добавления товара"
    )

    title = models.CharField(max_length=100, verbose_name="Название товара")

    description = models.TextField(blank=True, verbose_name="Описание товара")

    free_delivery = models.BooleanField(
        default=False, verbose_name="Бесплатная доставка"
    )

    sort_index = models.IntegerField(default=0, verbose_name="Индекс сортировки")

    sold_count = models.IntegerField(default=0, verbose_name="Количество покупок")

    limited_edition = models.BooleanField(
        default=False, verbose_name="Ограниченный тираж"
    )

    is_deleted = models.BooleanField(default=False, verbose_name="Мягко удалён")

    tags = models.ManyToManyField("Tag", related_name="products", verbose_name="Теги")

    reviews = models.IntegerField(default=0, verbose_name="Количество отзывов")

    rating = models.DecimalField(
        default=0,
        max_digits=3,
        decimal_places=2,
        verbose_name="Рейтинг товара",
        validators=[MinValueValidator(0), MaxValueValidator(5)],
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

    Используется:
    - для отображения галереи товара на фронтенде
    - в API каталога (вложенные изображения)

    Поля:
    - src — файл изображения
    - alt — описание изображения (для SEO и доступности)
    """

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )

    src = models.ImageField(
        upload_to="product/", verbose_name="Файл изображения товара"
    )

    alt = models.CharField(max_length=128, verbose_name="Описание изображения")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Изображение товара: {self.product.title}"


class Tag(models.Model):
    """
    Модель тега товара.

    Используется для:
    - фильтрации товаров в каталоге
    - группировки товаров по признакам

    Примеры:
    - Gaming
    - SSD
    - Laptop

    Связь:
    - ManyToMany с Product
    """

    name = models.CharField(max_length=100, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        """
        Строковое представление тега.
        """
        return self.name


class Review(models.Model):
    """
    Модель отзывов о товаре.

    Хранит пользовательские отзывы и оценки.

    Особенности:
    - при создании/удалении отзыва автоматически обновляется:
        - количество отзывов (Product.reviews)
        - рейтинг товара (Product.rating)
      через сигналы (signals.py)

    Ограничения:
    - оценка (rate) от 1 до 5

    Используется для:
    - отображения отзывов на странице товара
    - расчёта рейтинга
    """

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="reviews_list",
        verbose_name="Товар",
    )
    author = models.CharField(max_length=100, verbose_name="Автор отзыва")
    email = models.EmailField(max_length=254, verbose_name="Email")
    text = models.TextField(verbose_name="Содержание отзыва")
    rate = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оценка"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-date"]

    def __str__(self):
        """
        Строковое представление отзыва.
        """
        return f"{self.author} → {self.product.title}"


class Specification(models.Model):
    """
    Модель характеристик товара.

    Используется для хранения технических параметров товара.

    Примеры:
    - "Процессор": "Intel i7"
    - "Оперативная память": "16GB"

    Связь:
    - один товар → много характеристик

    Используется на странице товара для отображения спецификаций.
    """

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="Товар",
    )
    name = models.CharField(max_length=100, verbose_name="Имя характеристики")

    value = models.TextField(verbose_name="Значение характеристики")

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        """
        Строковое представление имени характеристики.
        """

        return f"{self.product.title} — {self.name}: {self.value}"


class Sale(models.Model):
    """
    Модель акции (скидки) на товар.

    Позволяет задать временную акцию с отдельной ценой.

    Особенности:
    - акция действует только в диапазоне дат (date_from — date_to)
    - валидируется:
        - дата окончания > даты начала
        - цена акции < обычной цены товара

    Логика:
    - метод clean() выполняет бизнес-валидацию
    - метод save() вызывает full_clean() перед сохранением

    Свойства:
    - is_current — активна ли акция в текущий момент

    Используется:
    - в API каталога (раздел "sales")
    - для отображения скидок на фронтенде
    """

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="sales", verbose_name="Товар"
    )

    title = models.CharField(max_length=100, verbose_name="Название акции")

    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена со скидкой"
    )

    date_from = models.DateTimeField(verbose_name="Дата начала акции")

    date_to = models.DateTimeField(verbose_name="Дата окончания акции")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания акции"
    )

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        """
        Строковое представление имени акции.
        """

        return f"{self.title} ({self.product.title})"

    def clean(self):
        errors = {}

        # Проверка даьы
        if self.date_to <= self.date_from:
            errors["date_to"] = "Дата окончания должна быть позже даты начала"

        # проверка цены акции
        if self.product and self.sale_price >= self.product.price:
            errors["sale_price"] = "Цена акции должна быть меньше цены товара"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_current(self):
        now = timezone.now()
        return self.date_from <= now <= self.date_to
