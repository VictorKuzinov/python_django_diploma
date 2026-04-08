from urllib.parse import parse_qs, urlparse

from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalog.models import Category, Product, Sale, Tag
from apps.catalog.serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
    SaleSerializer,
    TagSerializer,
)

from .pagination import CatalogPagination, SalePagination


class CategoryListView(ListAPIView):
    """
    API-представление списка категорий каталога.

    Возвращает только активные корневые категории.
    Для каждой категории также подгружаются активные дочерние категории.

    Используется:
    - для отображения меню категорий на фронтенде
    - для построения навигации по каталогу
    """

    serializer_class = CategorySerializer
    queryset = (
        Category.objects.select_related("parent")
        .filter(parent=None, is_active=True)
        .prefetch_related(
            Prefetch("children", queryset=Category.objects.filter(is_active=True))
        )
    )


class CatalogListView(ListAPIView):
    """
    API-представление каталога товаров.

    Поддерживает:
    - пагинацию
    - фильтрацию по названию, цене, наличию, бесплатной доставке и тегам
    - сортировку по цене, рейтингу, количеству отзывов и дате

    Особенности:
    - исключает мягко удалённые товары
    - исключает товары из неактивных категорий
    - содержит fallback-логику для получения фильтра по названию
      из HTTP_REFERER, если фронтенд не передал filter[name]
    """

    serializer_class = ProductSerializer
    pagination_class = CatalogPagination

    def get_queryset(self):
        """
        Формирует queryset товаров с учётом фильтрации и сортировки.
        """
        queryset = Product.objects.filter(
            is_deleted=False, category__is_active=True
        ).order_by("-date")

        name = self.request.query_params.get("filter[name]")
        min_price = self.request.query_params.get("filter[minPrice]")
        max_price = self.request.query_params.get("filter[maxPrice]")
        free_delivery = self.request.query_params.get("filter[freeDelivery]")
        available = self.request.query_params.get("filter[available]")
        tags = self.request.query_params.getlist("tags[]")
        sort = self.request.query_params.get("sort")
        sort_type = self.request.query_params.get("sortType")

        # В норме фронтенд должен передавать filter[name] в query-параметрах.
        # Этот блок используется как временный fallback.
        if not name:
            referer = self.request.META.get("HTTP_REFERER", "")
            if referer:
                parsed_url = urlparse(referer)
                referer_params = parse_qs(parsed_url.query)
                name = referer_params.get("filter", [""])[0]

        if name:
            queryset = queryset.filter(title__icontains=name)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if free_delivery == "true":
            queryset = queryset.filter(free_delivery=True)

        if available == "true":
            queryset = queryset.filter(count__gt=0)

        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()

        allowed_sort_fields = {
            "price": "price",
            "rating": "rating",
            "reviews": "reviews",
            "date": "date",
        }

        if sort in allowed_sort_fields:
            field = allowed_sort_fields[sort]
            if sort_type == "dec":
                field = f"-{field}"
            queryset = queryset.order_by(field)

        return queryset


class TagListView(ListAPIView):
    """
    API-представление списка тегов.

    Используется для фильтрации товаров на фронтенде.
    """

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class ProductDetailView(RetrieveAPIView):
    """
    API-представление детальной информации о товаре.

    Возвращает:
    - основные данные товара
    - изображения
    - теги
    - отзывы
    - характеристики

    Исключает:
    - мягко удалённые товары
    - товары из неактивных категорий
    """

    serializer_class = ProductDetailSerializer
    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("images", "tags", "reviews_list", "specifications")
        .filter(is_deleted=False, category__is_active=True)
    )


class ReviewCreateView(CreateAPIView):
    """
    API-представление для создания отзыва о товаре.

    Доступ:
    - только для авторизованных пользователей

    Особенности:
    - author и email не берутся из запроса
    - author и email подставляются автоматически
      из текущего пользователя
    - после создания возвращается обновлённый список отзывов товара
    """

    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Создаёт новый отзыв и возвращает актуальный список отзывов.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = serializer.save(
            product_id=self.kwargs["pk"],
            author=request.user.get_full_name() or request.user.username,
            email=request.user.email,
        )

        reviews = review.product.reviews_list.all()
        response_serializer = ReviewSerializer(reviews, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ProductPopularView(ListAPIView):
    """
    API-представление списка популярных товаров.

    Логика выборки:
    - только активные товары из активных категорий
    - сортировка по sort_index
    - при равенстве sort_index — по sold_count
    - ограничение до 8 товаров
    """

    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Возвращает queryset популярных товаров.
        """
        return Product.objects.filter(
            is_deleted=False,
            category__is_active=True,
        ).order_by("sort_index", "-sold_count")[:8]


class ProductLimitedView(ListAPIView):
    """
    API-представление списка товаров с ограниченным тиражом.

    Возвращает до 16 товаров с флагом limited_edition=True.
    """

    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Возвращает queryset товаров ограниченного тиража.
        """
        return Product.objects.filter(
            is_deleted=False,
            limited_edition=True,
            category__is_active=True,
        ).order_by("-date")[:16]


class SaleListView(ListAPIView):
    """
    API-представление списка активных акций.

    Возвращает только те акции:
    - у которых товар не удалён
    - товар находится в активной категории
    - текущая дата входит в диапазон действия акции

    Поддерживает пагинацию.
    """

    serializer_class = SaleSerializer
    pagination_class = SalePagination

    def get_queryset(self):
        """
        Возвращает queryset активных акций.
        """
        date_now = timezone.now()
        return Sale.objects.filter(
            product__is_deleted=False,
            product__category__is_active=True,
            date_from__lte=date_now,
            date_to__gte=date_now,
        ).order_by("-created_at")


class BannerListView(ListAPIView):
    """
    API-представление баннеров для главной страницы.

    Использует товары каталога в качестве источника данных для баннеров.
    Возвращает до 3 товаров:
    - не удалённых
    - из активных категорий
    """

    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Возвращает queryset товаров для баннеров.
        """
        queryset = (
            Product.objects.select_related("category")
            .prefetch_related(
                "images",
                "tags",
                "reviews_list",
            )
            .filter(is_deleted=False, category__is_active=True)
            .order_by("-date")
            .distinct()[:3]
        )
        return queryset
