from django.urls import path

from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.categories),
    path("banners/", views.banners),
    path("products/popular/", views.products_popular),
    path("products/limited/", views.products_limited),
]