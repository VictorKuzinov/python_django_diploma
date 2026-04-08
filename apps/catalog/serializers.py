from rest_framework import serializers

from .models import Category, Product, ProductImage, Review, Sale, Specification, Tag


class ImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор изображения категории.

    Используется для преобразования полей изображения категории
    в JSON-структуру, ожидаемую фронтендом Megano.

    Возвращает:
    - src — URL изображения
    - alt — альтернативное описание изображения
    """

    src = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["src", "alt"]

    def get_src(self, obj):
        """
        Возвращает полный URL изображения категории.
        """

        return obj.image.url if obj.image else None

    def get_alt(self, obj):
        """
        Возвращает описание изображения.
        """

        return obj.image_alt if obj.image_alt else ""


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор подкатегории каталога.

    Используется во вложенном виде внутри CategorySerializer.
    """

    image = ImageSerializer(source="*", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории каталога.

    Возвращает:
    - основную информацию о категории
    - изображение категории
    - вложенный список подкатегорий
    """

    image = ImageSerializer(source="*", read_only=True)
    subcategories = SubCategorySerializer(source="children", many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тега товара.

    Используется для отображения тегов в каталоге и на странице товара.
    """

    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор изображения товара.

    Преобразует объект ProductImage в JSON-структуру,
    используемую на фронтенде для галереи товара.
    """

    src = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["src", "alt"]

    def get_src(self, obj):
        """
        Возвращает относительный путь изображения товара.
        """

        return obj.src.url if obj.src else None


class ProductSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор товара.

    Используется:
    - в каталоге товаров
    - в корзине
    - в списках популярных и ограниченных товаров
    - в баннерах

    Дополнительно:
    - преобразует free_delivery -> freeDelivery
    - возвращает category как category_id
    - сериализует изображения и теги
    - приводит price и rating к float
    """

    freeDelivery = serializers.BooleanField(source="free_delivery")
    category = serializers.IntegerField(source="category_id")
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_price(self, obj):
        """
        Возвращает цену товара в формате float.
        """
        return float(obj.price) if obj.price is not None else None

    def get_rating(self, obj):
        """
        Возвращает рейтинг товара в формате float.
        """
        return float(obj.rating) if obj.rating is not None else None


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзыва о товаре.

    Используется для расчета рейтинг товара
    """

    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Review
        fields = [
            "author",
            "email",
            "text",
            "rate",
            "date",
        ]


class SpecificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор характеристики товара.

    Используется для вывода технических параметров
    на детальной странице товара.
    """

    class Meta:
        model = Specification
        fields = ["name", "value"]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор детальной информации о товаре.

    Используется на странице товара и возвращает:
    - базовые поля товара
    - изображения
    - теги
    - отзывы
    - характеристики
    - полное описание
    - рейтинг
    """

    freeDelivery = serializers.BooleanField(source="free_delivery")
    category = serializers.IntegerField(source="category_id")
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    fullDescription = serializers.CharField(source="description")
    specifications = SpecificationSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(source="reviews_list", many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        ]

    def get_price(self, obj):
        """
        Возвращает цену товара в формате float.
        """
        return float(obj.price) if obj.price is not None else None

    def get_rating(self, obj):
        """
        Возвращает рейтинг товара в формате float.
        """
        return float(obj.rating) if obj.rating is not None else None


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания отзыва.

    Принимает только поля, которые может вводить пользователь:
    - text
    - rate

    Поля author и email подставляются на backend автоматически
    на основе текущего авторизованного пользователя.
    """

    class Meta:
        model = Review
        fields = ["text", "rate"]


class SaleSerializer(serializers.ModelSerializer):
    """
    Сериализатор акции.

    Используется для вывода акций на странице sales.

    Возвращает:
        - id товара
        - обычную цену товара
        - цену по акции
        - даты начала и окончания акции
        - название товара
        - изображения товара
    """

    id = serializers.IntegerField(source="product.id", read_only=True)
    price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )
    salePrice = serializers.DecimalField(
        source="sale_price", max_digits=10, decimal_places=2, read_only=True
    )
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()
    title = serializers.CharField(source="product.title", read_only=True)
    images = ProductImageSerializer(source="product.images", many=True, read_only=True)

    class Meta:
        model = Sale
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]

    def get_dateFrom(self, obj):
        """
        Возвращает дату начала акции в формате MM-DD.
        """
        return obj.date_from.strftime("%m-%d")

    def get_dateTo(self, obj):
        """
        Возвращает дату окончания акции в формате MM-DD.
        """
        return obj.date_to.strftime("%m-%d")

    def get_price(self, obj):
        return float(obj.price) if obj.price is not None else None

    def get_sale_price(self, obj):
        return float(obj.salePrice) if obj.salePrice is not None else None
