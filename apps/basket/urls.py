from django.urls import path
from . import views

urlpatterns = [
    path("basket/", views.basket),
    path("basket", views.basket),
]