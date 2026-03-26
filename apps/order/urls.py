from django.urls import path

from .views import OrderView

urlpatterns = [
    path("orders",
         OrderView.as_view({
             'get': 'list',
             'post': 'create',
         }),
         name = "order"
    ),
    path("orders/",
         OrderView.as_view({
             'get': 'list',
             'post': 'create',
         }),
    ),
    path("orders/<int:pk>",
         OrderView.as_view({
        'get': 'retrieve',
        'post': 'confirm',
         }),
         name="order-detail"
    ),
    path("order/<int:pk>",
         OrderView.as_view({
        'get': 'retrieve',
        'post': 'confirm',
         }),
    ),
]