from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.utils import timezone

from .models import (
    Order,
    OrderItem,
    Product,
    DeliverySettings,
)
from apps.catalog.models import Sale
from .serializers import OrderSerializer


class OrderView(ViewSet):
    def list(self, request):
        if not request.user.is_authenticated:
            return Response([], status=400)

        orders = Order.objects.filter(user=request.user, is_deleted=False)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data, status=200)

    def create(self, request):
        basket = request.session.get("basket", {})
        if not basket:
            return Response({"error": "Basket is empty"}, status=400)
        product_ids = [int(pid) for pid in basket.keys()]
        products = Product.objects.filter(id__in=product_ids)

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None
        )
        if request.user.is_authenticated:
            order.email = request.user.email
            order.full_name = request.user.username or request.user.first_name

        order.total_cost = 0
        date_now = timezone.now()

        for product in products:
            count = basket.get(str(product.id), 0)
            active_sale = Sale.objects.filter(product=product, date_from__lte=date_now, date_to__gte=date_now).first()
            if active_sale:
                actual_price = active_sale.sale_price
            else:
                actual_price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                price=actual_price,
                count=count
            )

            order.total_cost += actual_price * count
        order.save()
        return Response({"orderId": order.id}, status=200)

    def retrieve(self, request, pk=None):
        order = get_object_or_404(Order, id=pk)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=200)

    def confirm(self, request, pk=None):
        order = get_object_or_404(Order, id=pk)

        order.full_name = request.data.get("fullName", "") or ""
        order.email = request.data.get("email")
        order.phone = request.data.get("phone")
        order.delivery_type = request.data.get("deliveryType", order.delivery_type)
        order.payment_type = request.data.get("paymentType", order.payment_type)
        order.city = request.data.get("city", "") or ""
        order.address = request.data.get("address", "") or ""

        settings = DeliverySettings.objects.first()

        if not settings:
            express_price = 500
            normal_price = 200
            threshold = 2000
        else:
            express_price = settings.express_delivery_price
            normal_price = settings.normal_delivery_price
            threshold = settings.free_delivery_threshold

        items_total = sum(item.price * item.count for item in order.items.all())

        if order.delivery_type == "express":
            delivery_cost = express_price
        else:
            delivery_cost = normal_price if items_total < threshold else 0

        order.total_cost = items_total + delivery_cost
        order.save()

        return Response({"orderId": order.id}, status=200)
