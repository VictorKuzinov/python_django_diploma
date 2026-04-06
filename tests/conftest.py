import pytest
from django.utils import timezone

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.catalog.models import Category, Product, Sale, Tag, Review
from apps.order.models import Order, OrderItem, DeliverySettings
from apps.userprofile.models import Profile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="test_user",
        email="test@example.com",
        password="123456",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def category(db):
    return Category.objects.create(
        title="Тест категория"
    )


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        category=category,
        title="Тест товар",
        price=1000,
        count=10,
        description="Описание",
    )


@pytest.fixture
def delivery_settings(db):
    return DeliverySettings.objects.create(
        express_delivery_price=500,
        normal_delivery_price=200,
        free_delivery_threshold=2000,
    )

@pytest.fixture
def sale(db, product):
    return Sale.objects.create(
        product=product,
        title="Тестовая акция",
        sale_price=800,
        date_from=timezone.now() - timezone.timedelta(days=1),
        date_to=timezone.now() + timezone.timedelta(days=1),
    )


@pytest.fixture
def basket_with_product(api_client, product):
    session = api_client.session
    session["basket"] = {str(product.id): 2}
    session.save()
    return api_client


@pytest.fixture
def order(db, user, product):
    order = Order.objects.create(
        user=user,
        full_name="Иван Покупатель",
        email="test@example.com",
        phone="+79990000000",
        delivery_type="normal",
        payment_type="online",
        city="Москва",
        address="ул. Тестовая, 1",
        total_cost=1000,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        price=1000,
        count=1,
    )
    return order

@pytest.fixture
def child_category(db, category):
    return Category.objects.create(
        title="Дочерняя категория",
        parent=category,
        is_active=True,
    )


@pytest.fixture
def inactive_category(db):
    return Category.objects.create(
        title="Неактивная категория",
        parent=None,
        is_active=False,
    )


@pytest.fixture
def tag(db):
    return Tag.objects.create(name="Тестовый тег")


@pytest.fixture
def tagged_product(db, category, tag):
    product = Product.objects.create(
        category=category,
        title="Товар с тегом",
        price=1500,
        count=5,
        description="Описание товара с тегом",
        free_delivery=True,
        sort_index=2,
        sold_count=3,
        limited_edition=False,
        reviews=1,
        rating=4.5,
        is_deleted=False,
    )
    product.tags.add(tag)
    return product


@pytest.fixture
def limited_product(db, category):
    return Product.objects.create(
        category=category,
        title="Ограниченный товар",
        price=2000,
        count=2,
        description="Limited товар",
        free_delivery=False,
        sort_index=3,
        sold_count=10,
        limited_edition=True,
        reviews=0,
        rating=5,
        is_deleted=False,
    )


@pytest.fixture
def deleted_product(db, category):
    return Product.objects.create(
        category=category,
        title="Удалённый товар",
        price=900,
        count=1,
        description="Удалённый товар",
        free_delivery=False,
        sort_index=4,
        sold_count=1,
        limited_edition=False,
        reviews=0,
        rating=1,
        is_deleted=True,
    )


@pytest.fixture
def inactive_category_product(db, inactive_category):
    return Product.objects.create(
        category=inactive_category,
        title="Товар в неактивной категории",
        price=1100,
        count=3,
        description="Скрытый товар",
        free_delivery=False,
        sort_index=5,
        sold_count=2,
        limited_edition=False,
        reviews=0,
        rating=3,
        is_deleted=False,
    )


@pytest.fixture
def active_sale(db, product):
    return Sale.objects.create(
        title="Активная акция",
        product=product,
        sale_price=800,
        date_from=timezone.now() - timezone.timedelta(days=1),
        date_to=timezone.now() + timezone.timedelta(days=1),
    )


@pytest.fixture
def expired_sale(db, product):
    return Sale.objects.create(
        title="Завершённая акция",
        product=product,
        sale_price=700,
        date_from=timezone.now() - timezone.timedelta(days=10),
        date_to=timezone.now() - timezone.timedelta(days=5),
    )

@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username="second_user",
        email="second@example.com",
        password="123456",
        first_name="Петр",
        last_name="Второй",
    )


@pytest.fixture
def another_profile(db, another_user):
    return Profile.objects.create(
        user=another_user,
        fullName="Петр Второй",
        phone="+79990000001",
    )


@pytest.fixture
def image_file():
    return SimpleUploadedFile(
        name="avatar.jpg",
        content=b"fake-image-content",
        content_type="image/jpeg",
    )


@pytest.fixture
def text_file():
    return SimpleUploadedFile(
        name="notes.txt",
        content=b"not-an-image",
        content_type="text/plain",
    )


@pytest.fixture
def large_image_file():
    return SimpleUploadedFile(
        name="big_avatar.jpg",
        content=b"a" * (2 * 1024 * 1024 + 1),
        content_type="image/jpeg",
    )

@pytest.fixture
def unpaid_order(db, user, product):
    from apps.order.models import Order, OrderItem, OrderStatus

    order = Order.objects.create(
        user=user,
        full_name="Иван Покупатель",
        email="test@example.com",
        phone="+79990000000",
        delivery_type="normal",
        payment_type="online",
        city="Москва",
        address="ул. Тестовая, 1",
        status=OrderStatus.NEW,
        total_cost=1000,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        price=1000,
        count=1,
    )

    return order