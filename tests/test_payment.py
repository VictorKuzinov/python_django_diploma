import pytest
from rest_framework import status

from apps.order.models import OrderStatus

pytestmark = pytest.mark.django_db


def test_payment_with_valid_even_number_marks_order_paid_and_clears_basket(
    auth_client, unpaid_order
):
    """
    Проверяем, что корректный номер счета помечает заказ как оплаченный
    и очищает корзину.
    """
    session = auth_client.session
    session["basket"] = {"1": 2}
    session.save()

    response = auth_client.post(
        f"/api/payment/{unpaid_order.id}",
        data={"number": "12345678"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    unpaid_order.refresh_from_db()
    assert unpaid_order.status == OrderStatus.PAID
    assert unpaid_order.payment_error == ""

    session = auth_client.session
    assert session["basket"] == {}


def test_payment_with_empty_number_returns_400_and_marks_order_failed(
    auth_client, unpaid_order
):
    """
    Проверяем, что пустой номер счета возвращает 400
    и помечает заказ как неуспешный.
    """
    response = auth_client.post(
        f"/api/payment/{unpaid_order.id}",
        data={"number": ""},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    unpaid_order.refresh_from_db()
    assert unpaid_order.status == OrderStatus.FAILED
    assert unpaid_order.payment_error == "Платеж не прошел, неверно указан счет"


def test_payment_with_too_long_number_returns_400(auth_client, unpaid_order):
    """
    Проверяем, что номер счета длиннее 8 символов отклоняется.
    """
    response = auth_client.post(
        f"/api/payment/{unpaid_order.id}",
        data={"number": "123456789"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    unpaid_order.refresh_from_db()
    assert unpaid_order.status == OrderStatus.FAILED
    assert unpaid_order.payment_error == "Платеж не прошел, неверно указан счет"


def test_payment_with_non_digit_number_returns_400(auth_client, unpaid_order):
    """
    Проверяем, что нечисловой номер счета отклоняется.
    """
    response = auth_client.post(
        f"/api/payment/{unpaid_order.id}",
        data={"number": "12ab56"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    unpaid_order.refresh_from_db()
    assert unpaid_order.status == OrderStatus.FAILED
    assert unpaid_order.payment_error == "Платеж не прошел, неверно указан счет"


def test_payment_with_odd_last_digit_returns_400(auth_client, unpaid_order):
    """
    Проверяем, что счет с нечетной последней цифрой отклоняется.
    """
    response = auth_client.post(
        f"/api/payment/{unpaid_order.id}",
        data={"number": "1234567"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    unpaid_order.refresh_from_db()
    assert unpaid_order.status == OrderStatus.FAILED
    assert (
        unpaid_order.payment_error == "Платеж не прошел, из-за ошибки валидации счета"
    )


def test_payment_with_zero_last_digit_returns_400(auth_client, unpaid_order):
    """
    Проверяем, что счет, оканчивающийся на 0, отклоняется.
    """
    response = auth_client.post(
        f"/api/payment/{unpaid_order.id}",
        data={"number": "12345670"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    unpaid_order.refresh_from_db()
    assert unpaid_order.status == OrderStatus.FAILED
    assert (
        unpaid_order.payment_error == "Платеж не прошел, из-за ошибки валидации счета"
    )


def test_payment_for_nonexistent_order_returns_404(auth_client):
    """
    Проверяем, что оплата несуществующего заказа возвращает 404.
    """
    response = auth_client.post(
        "/api/payment/999999",
        data={"number": "12345678"},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
