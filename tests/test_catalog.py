from rest_framework import status


CATEGORIES_URL = "/api/categories"
CATALOG_URL = "/api/catalog"
TAGS_URL = "/api/tags"
POPULAR_URL = "/api/products/popular"
LIMITED_URL = "/api/products/limited"
SALES_URL = "/api/sales"


def test_get_categories_returns_only_active_root_categories(api_client, category, child_category, inactive_category):
    """
    Проверяем, что categories возвращает только активные корневые категории.
    """
    response = api_client.get(CATEGORIES_URL)

    assert response.status_code == status.HTTP_200_OK
    returned_ids = [item["id"] for item in response.data]

    assert category.id in returned_ids
    assert child_category.id not in returned_ids
    assert inactive_category.id not in returned_ids


def test_get_catalog_returns_active_products_only(api_client, product, deleted_product, inactive_category_product):
    """
    Проверяем, что каталог возвращает только неудалённые товары
    из активных категорий.
    """
    response = api_client.get(CATALOG_URL)

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    returned_ids = [item["id"] for item in items]

    assert product.id in returned_ids
    assert deleted_product.id not in returned_ids
    assert inactive_category_product.id not in returned_ids


def test_catalog_filters_by_name(api_client, product):
    """
    Проверяем фильтрацию каталога по названию товара.
    """
    response = api_client.get(CATALOG_URL, {"filter[name]": product.title})

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    assert len(items) >= 1
    assert items[0]["id"] == product.id


def test_catalog_filters_by_min_price(api_client, product, tagged_product):
    """
    Проверяем фильтрацию по минимальной цене.
    """
    response = api_client.get(CATALOG_URL, {"filter[minPrice]": 1200})

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    returned_ids = [item["id"] for item in items]

    assert tagged_product.id in returned_ids
    assert product.id not in returned_ids


def test_catalog_filters_by_free_delivery(api_client, product, tagged_product):
    """
    Проверяем фильтрацию товаров с бесплатной доставкой.
    """
    response = api_client.get(CATALOG_URL, {"filter[freeDelivery]": "true"})

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    returned_ids = [item["id"] for item in items]

    assert tagged_product.id in returned_ids
    assert product.id not in returned_ids


def test_catalog_filters_by_available(api_client, product):
    """
    Проверяем фильтрацию только доступных товаров.
    """
    response = api_client.get(CATALOG_URL, {"filter[available]": "true"})

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    assert product.id in [item["id"] for item in items]


def test_catalog_filters_by_tag(api_client, tagged_product, tag):
    """
    Проверяем фильтрацию каталога по тегу.
    """
    response = api_client.get(CATALOG_URL, {"tags[]": tag.id})

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    returned_ids = [item["id"] for item in items]

    assert tagged_product.id in returned_ids


def test_catalog_sort_by_price_desc(api_client, product, tagged_product):
    """
    Проверяем сортировку каталога по цене по убыванию.
    """
    response = api_client.get(CATALOG_URL, {"sort": "price", "sortType": "dec"})

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]

    assert items[0]["price"] >= items[-1]["price"]


def test_get_tags_returns_200(api_client, tag):
    """
    Проверяем, что список тегов доступен.
    """
    response = api_client.get(TAGS_URL)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert response.data[0]["name"] == tag.name


def test_get_product_detail_returns_200(api_client, product):
    """
    Проверяем, что детальная страница товара доступна.
    """
    response = api_client.get(f"/api/product/{product.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == product.id


def test_deleted_product_detail_returns_404(api_client, deleted_product):
    """
    Проверяем, что мягко удалённый товар недоступен.
    """
    response = api_client.get(f"/api/product/{deleted_product.id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_popular_products_returns_200(api_client, product, deleted_product, inactive_category_product):
    """
    Проверяем, что popular возвращает только допустимые товары.
    """
    response = api_client.get(POPULAR_URL)

    assert response.status_code == status.HTTP_200_OK
    returned_ids = [item["id"] for item in response.data]

    assert product.id in returned_ids
    assert deleted_product.id not in returned_ids
    assert inactive_category_product.id not in returned_ids


def test_get_limited_products_returns_only_limited(api_client, limited_product, product):
    """
    Проверяем, что limited возвращает только товары limited_edition=True.
    """
    response = api_client.get(LIMITED_URL)

    assert response.status_code == status.HTTP_200_OK
    returned_ids = [item["id"] for item in response.data]

    assert limited_product.id in returned_ids
    assert product.id not in returned_ids


def test_get_sales_returns_only_active_sales(api_client, active_sale, expired_sale):
    """
    Проверяем, что sales возвращает только активные акции.
    """
    response = api_client.get(SALES_URL)

    assert response.status_code == status.HTTP_200_OK
    items = response.data["items"]
    returned_ids = [item["id"] for item in items]

    assert active_sale.id in returned_ids
    assert expired_sale.id not in returned_ids


def test_authenticated_user_can_create_review(auth_client, product):
    """
    Проверяем, что авторизованный пользователь может оставить отзыв.
    """
    response = auth_client.post(
        f"/api/product/{product.id}/reviews",
        data={
            "text": "Отличный товар",
            "rate": 5,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert response.data[0]["rate"] == 5


def test_anonymous_user_cannot_create_review(api_client, product):
    """
    Проверяем, что неавторизованный пользователь не может оставить отзыв.
    """
    response = api_client.post(
        f"/api/product/{product.id}/reviews",
        data={
            "text": "Анонимный отзыв",
            "rate": 4,
        },
        format="json",
    )

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )