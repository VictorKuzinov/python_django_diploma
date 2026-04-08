from rest_framework import status

# Базовый URL корзины
BASKET_URL = "/api/basket"


def test_get_empty_basket(api_client):
    """
    Проверяем, что при пустой сессии корзина возвращает пустой список.
    """
    response = api_client.get(BASKET_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_add_product_to_basket(api_client, product):
    """
    Проверяем, что товар добавляется в корзину.
    """
    response = api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 1},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert response.data[0]["id"] == product.id
    assert response.data[0]["count"] == 1


def test_add_same_product_twice_increases_count(api_client, product):
    """
    Проверяем, что при повторном добавлении товара количество увеличивается.
    """
    api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 1},
        format="json",
    )

    response = api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 2},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == product.id
    assert response.data[0]["count"] == 3


def test_patch_product_count_in_basket(api_client, product):
    """
    Проверяем, что PATCH обновляет количество товара.
    """
    api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 1},
        format="json",
    )

    response = api_client.patch(
        BASKET_URL,
        data={"id": product.id, "count": 5},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == product.id
    assert response.data[0]["count"] == 5


def test_patch_with_zero_count_removes_product(api_client, product):
    """
    Проверяем, что при count=0 товар удаляется из корзины.
    """
    api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 2},
        format="json",
    )

    response = api_client.patch(
        BASKET_URL,
        data={"id": product.id, "count": 0},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_delete_product_from_basket_without_count_removes_it(api_client, product):
    """
    Проверяем, что DELETE без count удаляет товар полностью.
    """
    api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 2},
        format="json",
    )

    response = api_client.delete(
        BASKET_URL,
        data={"id": product.id},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_delete_product_from_basket_with_count_decreases_quantity(api_client, product):
    """
    Проверяем, что DELETE с count уменьшает количество товара.
    """
    api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": 3},
        format="json",
    )

    response = api_client.delete(
        BASKET_URL,
        data={"id": product.id, "count": 1},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == product.id
    assert response.data[0]["count"] == 2


def test_create_without_product_id_returns_400(api_client):
    """
    Проверяем, что POST без id возвращает 400.
    """
    response = api_client.post(
        BASKET_URL,
        data={"count": 1},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_patch_without_product_id_returns_400(api_client):
    """
    Проверяем, что PATCH без id возвращает 400.
    """
    response = api_client.patch(
        BASKET_URL,
        data={"count": 2},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_without_product_id_returns_400(api_client):
    """
    Проверяем, что DELETE без id возвращает 400.
    """
    response = api_client.delete(
        BASKET_URL,
        data={"count": 1},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_invalid_count_defaults_to_1(api_client, product):
    """
    Проверяем, что некорректный count заменяется на 1.
    """
    response = api_client.post(
        BASKET_URL,
        data={"id": product.id, "count": "abc"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["count"] == 1
