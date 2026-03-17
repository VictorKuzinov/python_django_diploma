from urllib.parse import urlparse, parse_qs

from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.catalog.models import Category, Product, Tag
from apps.catalog.serializers import (
    CategorySerializer,
    ProductSerializer,
    TagSerializer,
)

from apps.catalog.pagination import CatalogPagination
class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = (
            Category.objects
            .select_related("parent")
            .filter(parent=None)
            .prefetch_related("children")
    )


class CatalogListView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CatalogPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        name = self.request.query_params.get("filter[name]")
        min_price = self.request.query_params.get("filter[minPrice]")
        max_price = self.request.query_params.get("filter[maxPrice]")
        free_delivery = self.request.query_params.get("filter[freeDelivery]")
        available = self.request.query_params.get("filter[available]")
        tags = self.request.query_params.getlist("tags[]")
        sort = self.request.query_params.get("sort")
        sort_type = self.request.query_params.get("sortType")

        # В норме фронтенд должен передавать filter[name] в query-параметрах,
        # этот код — временный fallback.

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
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


@api_view(["GET"])
def banners(request):
    return Response([])


@api_view(["GET"])
def products_popular(request):
    return Response([])


@api_view(["GET"])
def products_limited(request):
    return Response([])