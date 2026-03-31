from itertools import product

from rest_framework import serializers
from .models import Category, Tag, ProductImage, Product, Review, Specification, Sale


class ImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор изображения категории.

    Преобразует объект Изображение Category в JSON-структуру,
    ожидаемую фронтендом Megano.
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
    """

    image = ImageSerializer(source="*", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image"]


class CategorySerializer(serializers.ModelSerializer):
    """
         Сериализатор категории каталога.
    """

    image = ImageSerializer(source="*", read_only=True)
    subcategories = SubCategorySerializer(source="children", many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class TagSerializer(serializers.ModelSerializer):
    """
        Сериализатор тега.
    """

    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProductImageSerializer(serializers.ModelSerializer):
    """
       Сериализатор изображения товара.

       Преобразует объект ProductImage в JSON-структуру,
       ожидаемую фронтендом Megano.
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
        Сериализатор товара.
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
        return float(obj.price) if obj.price is not None else None

    def get_rating(self, obj):
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
        Сериализатор характеристик товара.
    """
    class Meta:
        model = Specification
        fields = ["name", "value"]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор детальной информации о товаре.
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
        return float(obj.price) if obj.price is not None else None

    def get_rating(self, obj):
        return float(obj.rating) if obj.rating is not None else None


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["text", "rate"]


class SaleSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source="product.id", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    salePrice = serializers.DecimalField(source="sale_price", max_digits=10, decimal_places=2, read_only=True)
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()
    title = serializers.CharField(source="product.title", read_only=True)
    images = ProductImageSerializer(source="product.images", many=True,read_only=True)


    class Meta:
        model = Sale
        fields = ["id",
                  "price",
                  "salePrice",
                  "dateFrom",
                  "dateTo",
                  "title",
                  "images"
        ]

    def get_dateFrom(self, obj):
        return obj.date_from.strftime("%m-%d")

    def get_dateTo(self, obj):
        return obj.date_to.strftime("%m-%d")

    def get_price(self, obj):
        return float(obj.price) if obj.price is not None else None

    def get_sale_price(self, obj):
        return float(obj.salePrice) if obj.salePrice is not None else None
