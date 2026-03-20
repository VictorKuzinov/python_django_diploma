from django.urls import path
from . import views
from .views import (
    CategoryListView,
    CatalogListView,
    TagListView,
    ProductDetailView,
    ReviewCreateView,
    ProductPopularView,
    ProductLimitedView,
)

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/", CategoryListView.as_view()),
    path("catalog", CatalogListView.as_view(), name="catalog"),
    path("catalog/", CatalogListView.as_view()),
    path("tags", TagListView.as_view(), name="tags"),
    path("tags/", TagListView.as_view()),
    path("banners/", views.banners),
    path("banners", views.banners),
    path("product/<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path("product/<int:pk>/", ProductDetailView.as_view()),
    path("product/<int:pk>/reviews", ReviewCreateView.as_view(), name="review-create"),
    path("product/<int:pk>/reviews/", ReviewCreateView.as_view()),
    path("products/popular", ProductPopularView.as_view(), name="product-popular"),
    path("products/popular/", ProductPopularView.as_view()),
    path("products/limited", ProductLimitedView.as_view(), name="product-limited"),
    path("products/limited/", ProductLimitedView.as_view()),
]