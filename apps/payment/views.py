from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.order.models import Order, OrderStatus


class PaymentView(APIView):
    """
    API-представление для обработки оплаты заказа.

    Логика оплаты:
    - номер счёта должен содержать только цифры
    - длина номера не должна превышать 8 символов
    - если последняя цифра чётная и не равна 0 — оплата успешна
    - если последняя цифра нечётная или равна 0 — оплата отклоняется

    При успешной оплате:
    - заказ получает статус PAID
    - текст ошибки оплаты очищается
    - корзина пользователя очищается

    При неуспешной оплате:
    - заказ получает статус FAILED
    - сохраняется текст ошибки в поле payment_error
    """

    def post(self, request, pk=None, *args, **kwargs):
        """
        Обрабатывает оплату заказа по его идентификатору.

        Ожидает:
        - number: номер счёта/карты

        Возвращает:
        - 200, если оплата прошла успешно
        - 400, если номер невалиден или оплата отклонена
        """
        order = get_object_or_404(Order, id=pk)
        number = str(request.data.get("number", ""))

        if not ((len(number) > 0 and len(number) <= 8) and number.isdigit()):
            order.status = OrderStatus.FAILED
            order.payment_error = "Платеж не прошел, неверно указан счет"
            order.save()
            return Response(status=400)

        end_symbol = int(number[-1])

        if (end_symbol % 2 == 0) and (end_symbol != 0):
            order.status = OrderStatus.PAID
            order.payment_error = ""
            order.save()

            request.session["basket"] = {}
            request.session.modified = True
        else:
            order.status = OrderStatus.FAILED
            order.payment_error = "Платеж не прошел, из-за ошибки валидации счета"
            order.save()
            return Response(status=400)

        return Response(status=200)
