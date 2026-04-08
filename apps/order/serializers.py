from rest_framework import serializers

from apps.catalog.serializers import ProductSerializer

from .models import DeliverySettings, Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор заказа.

    Используется для:
    - списка заказов пользователя
    - детального просмотра заказа
    - передачи данных на этапах подтверждения и оплаты

    Особенности:
    - преобразует snake_case поля модели в camelCase для фронтенда Megano
    - возвращает состав заказа через products
    - подставляет цену и количество товара из OrderItem,
      чтобы сохранить состояние заказа на момент покупки
    - возвращает текущие настройки доставки
    """

    createdAt = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M")
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
        """
        Возвращает список товаров в составе заказа.

        Для каждого товара:
        - count подменяется значением из OrderItem
        - price подменяется зафиксированной ценой на момент заказа

        Это позволяет не зависеть от текущих значений товара в каталоге.
        """
        items = obj.items.all()
        products = []

        for item in items:
            product = item.product
            product.count = item.count  # подмена количества
            product.price = item.price  # подмена цены
            products.append(product)

        return ProductSerializer(products, many=True).data

    def get_totalCost(self, obj):
        """
        Возвращает итоговую стоимость заказа в формате float.
        """
        return float(obj.total_cost)

    def get_expressDeliveryPrice(self, obj):
        """
        Возвращает стоимость экспресс-доставки.

        Если настройки доставки отсутствуют, используется значение по умолчанию.
        """
        setting = DeliverySettings.objects.first()
        return float(setting.express_delivery_price) if setting else 500

    def get_normalDeliveryPrice(self, obj):
        """
        Возвращает стоимость обычной доставки.

        Если настройки доставки отсутствуют, используется значение по умолчанию.
        """
        setting = DeliverySettings.objects.first()
        return float(setting.normal_delivery_price) if setting else 200

    def get_freeDeliveryThreshold(self, obj):
        """
        Возвращает порог бесплатной доставки.

        Если настройки доставки отсутствуют, используется значение по умолчанию.
        """
        setting = DeliverySettings.objects.first()
        return float(setting.free_delivery_threshold) if setting else 2000
