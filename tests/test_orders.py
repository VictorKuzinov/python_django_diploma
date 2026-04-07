from rest_framework import status


ORDERS_URL = "/api/orders"


def test_get_orders_unauthorized_returns_400(api_client):
    """
    Проверяем, что список заказов для неавторизованного пользователя
    возвращает 400.
    """
    response = api_client.get(ORDERS_URL)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == []


def test_get_orders_authorized_returns_user_orders(auth_client, order):
    """
    Проверяем, что авторизованный пользователь может получить список
    своих заказов.
    """
    response = auth_client.get(ORDERS_URL)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert response.data[0]["id"] == order.id


def test_create_order_from_basket(api_client, basket_with_product):
    """
    Проверяем, что заказ создаётся из корзины и возвращает orderId.
    """
    response = basket_with_product.post(ORDERS_URL, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "orderId" in response.data


def test_create_order_from_empty_basket_returns_400(api_client):
    """
    Проверяем, что из пустой корзины заказ создать нельзя.
    """
    response = api_client.post(ORDERS_URL, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Basket is empty"


def test_create_order_applies_sale_price(api_client, product, sale):
    """
    Проверяем, что при наличии активной акции в OrderItem
    сохраняется sale_price, а не обычная цена товара.
    """
    session = api_client.session
    session["basket"] = {str(product.id): 2}
    session.save()

    response = api_client.post(ORDERS_URL, format="json")

    assert response.status_code == status.HTTP_200_OK
    order_id = response.data["orderId"]

    from apps.order.models import OrderItem

    item = OrderItem.objects.get(order_id=order_id, product=product)
    assert item.price == sale.sale_price
    assert item.count == 2


def test_retrieve_order_returns_200(auth_client, order):
    """
    Проверяем, что заказ можно получить по id.
    """
    response = auth_client.get(f"/api/orders/{order.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == order.id


def test_confirm_order_with_normal_delivery_adds_delivery_cost(auth_client, order, delivery_settings):
    """
    Проверяем, что при подтверждении заказа с обычной доставкой
    стоимость доставки добавляется к сумме заказа, если сумма товаров
    меньше порога бесплатной доставки.
    """
    response = auth_client.post(
        f"/api/orders/{order.id}",
        data={
            "fullName": "Иван Покупатель",
            "email": "test@example.com",
            "phone": "+79990000000",
            "deliveryType": "normal",
            "paymentType": "online",
            "city": "Москва",
            "address": "ул. Тестовая, 1",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["orderId"] == order.id

    order.refresh_from_db()
    assert order.total_cost == 1200


def test_confirm_order_with_express_delivery_adds_express_cost(auth_client, order, delivery_settings):
    """
    Проверяем, что при экспресс-доставке к сумме заказа
    добавляется express_delivery_price.
    """
    response = auth_client.post(
        f"/api/orders/{order.id}",
        data={
            "fullName": "Иван Покупатель",
            "email": "test@example.com",
            "phone": "+79990000000",
            "deliveryType": "express",
            "paymentType": "online",
            "city": "Москва",
            "address": "ул. Тестовая, 1",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    order.refresh_from_db()
    assert order.total_cost == 1500