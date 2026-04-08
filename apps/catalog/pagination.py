from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CatalogPagination(PageNumberPagination):
    """
    Кастомная пагинация для каталога товаров.

    Особенности:
    - соответствует формату ответа, ожидаемому фронтендом (Megano)
    - поддерживает параметр limit для задания размера страницы
    - использует currentPage вместо стандартного page

    Формат ответа:
    {
        "items": [...],
        "currentPage": int,
        "lastPage": int
    }
    """

    page_size = 20
    page_size_query_param = "limit"
    page_query_param = "currentPage"

    def get_paginated_response(self, data):
        """
        Формирует кастомный ответ пагинации.
        """
        return Response(
            {
                "items": data,
                "currentPage": self.page.number,
                "lastPage": self.page.paginator.num_pages,
            }
        )


class SalePagination(PageNumberPagination):
    """
    Кастомная пагинация для списка акций (Sale).

    Повторяет поведение CatalogPagination,
    но используется отдельно для логического разделения.

    Используется в endpoint:
    GET /api/sales
    """

    page_size = 20
    page_size_query_param = "limit"
    page_query_param = "currentPage"

    def get_paginated_response(self, data):
        """
        Формирует кастомный ответ пагинации.
        """
        return Response(
            {
                "items": data,
                "currentPage": self.page.number,
                "lastPage": self.page.paginator.num_pages,
            }
        )
