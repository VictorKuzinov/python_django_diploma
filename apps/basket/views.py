from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET", "POST"])
def basket(request):
    # базовая форма, чтобы фронт не падал
    return Response({"products": [], "totalCount": 0, "totalPrice": 0})
