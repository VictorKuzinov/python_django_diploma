from django.urls import path
from .views import BasketView

urlpatterns = [
    path("basket", BasketView.as_view({'get': 'list',
                                       'post': 'create',
                                       'delete': 'destroy',
                                       'patch': 'partial_update',
                                       }), name="basket"),
    path("basket/",BasketView.as_view({'get': 'list',
                                       'post': 'create',
                                       'delete': 'destroy',
                                       'patch': 'partial_update',
                                       })),
]