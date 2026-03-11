from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def categories(request):
    return Response([])


@api_view(["GET"])
def banners(request):
    return Response([])


@api_view(["GET"])
def products_popular(request):
    return Response([])


@api_view(["GET"])
def products_limited(request):
    return Response([])