from django.urls import path

from .views import (
    CategoryListView,
    CatalogListView,
    TagListView,
    ProductDetailView,
    ReviewCreateView,
    ProductPopularView,
    ProductLimitedView,
    SaleListView,
    BannerListView,
)

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/", CategoryListView.as_view()),
    path("catalog", CatalogListView.as_view(), name="catalog"),
    path("catalog/", CatalogListView.as_view()),
    path("tags", TagListView.as_view(), name="tags"),
    path("tags/", TagListView.as_view()),
    path("banners", BannerListView.as_view(), name='banners'),
    path("banners/", BannerListView.as_view()),
    path("product/<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path("product/<int:pk>/", ProductDetailView.as_view()),
    path("product/<int:pk>/reviews", ReviewCreateView.as_view(), name="review-create"),
    path("product/<int:pk>/reviews/", ReviewCreateView.as_view()),
    path("products/popular", ProductPopularView.as_view(), name="product-popular"),
    path("products/popular/", ProductPopularView.as_view()),
    path("products/limited", ProductLimitedView.as_view(), name="product-limited"),
    path("products/limited/", ProductLimitedView.as_view()),
    path("sales", SaleListView.as_view(), name="sale-list"),
    path("sales/", SaleListView.as_view()),
]