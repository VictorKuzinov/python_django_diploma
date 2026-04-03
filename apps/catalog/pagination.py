from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CatalogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    page_query_param = "currentPage"

    def get_paginated_response(self, data):

        return Response({
            "items": data,
            "currentPage": self.page.number,
            "lastPage": self.page.paginator.num_pages,
        })

class SalePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    page_query_param = "currentPage"

    def get_paginated_response(self, data):

        return Response({
            "items": data,
            "currentPage": self.page.number,
            "lastPage": self.page.paginator.num_pages,
        })
