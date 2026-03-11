# api/urls.py
from django.urls import include, path

urlpatterns = [
    path("", include("apps.authapp.urls")),
    path("", include("apps.catalog.urls")),
    path("", include("apps.basket.urls")),
    path("", include("apps.order.urls")),
    path("", include("apps.payment.urls")),
    path("", include("apps.userprofile.urls")),
    path("", include("apps.tags.urls")),
]