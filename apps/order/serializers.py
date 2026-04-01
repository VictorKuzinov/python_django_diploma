from rest_framework import serializers

from .models import Order, DeliverySettings
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
    expressDeliveryPrice = serializers.SerializerMethodField()
    normalDeliveryPrice = serializers.SerializerMethodField()
    freeDeliveryThreshold = serializers.SerializerMethodField()

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
            "expressDeliveryPrice",
            "normalDeliveryPrice",
            "freeDeliveryThreshold",
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

    def get_expressDeliveryPrice(self, obj):
        setting = DeliverySettings.objects.first()
        return setting.express_delivery_price if setting else 500

    def get_normalDeliveryPrice(self, obj):
        setting = DeliverySettings.objects.first()
        return setting.normal_delivery_price if setting else 200

    def get_freeDeliveryThreshold(self, obj):
        setting = DeliverySettings.objects.first()
        return setting.free_delivery_threshold if setting else 2000