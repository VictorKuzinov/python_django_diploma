from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.catalog.models import Product
from apps.catalog.serializers import ProductSerializer


class BasketView(ViewSet):
    """
    ViewSet для работы с корзиной пользователя.

    Корзина хранится в сессии пользователя (request.session) в виде словаря:
    {
        "product_id": count
    }

    Поддерживает операции:
    - получение содержимого корзины
    - добавление товара
    - изменение количества товара
    - удаление товара (полностью или частично)
    """

    def _serialize_basket(self, basket):
        """
        Преобразует корзину из session в сериализованный список товаров.

        Для каждого товара подменяет поле count значением из корзины.
        """
        if not basket:
            return []

        product_ids = [int(pid) for pid in basket]
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            product.count = basket.get(str(product.id), 0)

        serializer = ProductSerializer(products, many=True)
        return serializer.data

    def list(self, request):
        """
        Возвращает текущее содержимое корзины.

        GET /api/basket
        """
        basket = request.session.get("basket", {})
        return Response(self._serialize_basket(basket), status=status.HTTP_200_OK)

    def create(self, request):
        """
        Добавляет товар в корзину или увеличивает его количество.

        POST /api/basket

        Ожидает:
        {
            "id": product_id,
            "count": количество (опционально, по умолчанию 1)
        }
        """
        basket = request.session.get("basket", {})
        product_id = request.data.get("id")

        if not product_id:
            return Response({"basket": basket}, status=status.HTTP_400_BAD_REQUEST)

        product_id = str(product_id)
        count = request.data.get("count", 1)

        try:
            count = int(count)
        except (TypeError, ValueError):
            count = 1

        if count < 1:
            count = 1

        basket[product_id] = basket.get(product_id, 0) + count

        request.session["basket"] = basket
        request.session.modified = True

        return Response(self._serialize_basket(basket), status=status.HTTP_200_OK)

    def partial_update(self, request):
        """
        Обновляет количество товара в корзине.

        PATCH /api/basket

        Ожидает:
        {
            "id": product_id,
            "count": новое количество
        }

        Если count <= 0 — товар удаляется из корзины.
        """
        basket = request.session.get("basket", {})
        product_id = request.data.get("id")
        count = request.data.get("count")

        if not product_id:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        product_id = str(product_id)

        try:
            count = int(count)
        except (TypeError, ValueError):
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        if count <= 0:
            basket.pop(product_id, None)
        else:
            basket[product_id] = count

        request.session["basket"] = basket
        request.session.modified = True

        return Response(self._serialize_basket(basket), status=status.HTTP_200_OK)

    def destroy(self, request):
        """
        Удаляет товар из корзины.

        DELETE /api/basket

        Возможны два сценария:
        - если count не передан → товар удаляется полностью
        - если count передан → уменьшается количество

        Ожидает:
        {
            "id": product_id,
            "count": количество (опционально)
        }
        """
        basket = request.session.get("basket", {})
        product_id = request.data.get("id")
        count = request.data.get("count")

        if not product_id:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        product_id = str(product_id)

        if count is not None:
            try:
                count = int(count)
            except (TypeError, ValueError):
                count = 1

            if count < 1:
                count = 1

            current_count = basket.get(product_id, 0)
            new_count = current_count - count

            if new_count > 0:
                basket[product_id] = new_count
            else:
                basket.pop(product_id, None)
        else:
            basket.pop(product_id, None)

        request.session["basket"] = basket
        request.session.modified = True

        return Response(self._serialize_basket(basket), status=status.HTTP_200_OK)
