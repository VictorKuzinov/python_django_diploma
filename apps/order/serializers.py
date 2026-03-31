from django.template.base import kwarg_re
from rest_framework import serializers
from rest_framework.fields import ChoiceField

from .models import Order
from apps.catalog.serializers import ProductSerializer




class OrderSerializer(serializers.ModelSerializer):
    """
        Сериализатор заказа.
    """

    createdAt = serializers.DateTimeField(
        source="created_at",
        format="%Y-%m-%d %H:%M"
    )
    fullName = serializers.CharField(source="full_name")
    deliveryType = serializers.CharField(source="delivery_type")
    paymentType = serializers.CharField(source="payment_type")
    totalCost = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
    ]

    def get_products(self, obj):
        items = obj.items.all()
        products = []

        for item in items:
            product = item.product
            product.count = item.count # подмена количества
            product.price = item.price # подмена цены
            products.append(product)

        return ProductSerializer(products, many=True).data

    def get_totalCost(self, obj):
        return float(obj.total_cost)