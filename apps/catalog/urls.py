from django.urls import path
from . import views
from .views import (
    CategoryListView,
    CatalogListView,
    TagListView,
)

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/", CategoryListView.as_view()),
    path("catalog", CatalogListView.as_view(), name="catalog"),
    path("catalog/", CatalogListView.as_view()),
    path("tags", TagListView.as_view(), name="tags"),
    path("tags/", TagListView.as_view()),
    path("banners/", views.banners),
    path("products/popular/", views.products_popular),
    path("products/limited/", views.products_limited),
]