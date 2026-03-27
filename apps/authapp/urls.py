# apps/authapp/urls.py
from django.urls import path
from .views import SignUpView, SignInView, SignOutView

urlpatterns = [
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path("sign-up/", SignUpView.as_view()),
    path("sign-in", SignInView.as_view(), name="sign-in"),
    path("sign-in/", SignInView.as_view()),
    path("sign-out", SignOutView.as_view(), name="sign-out"),
    path("sign-out/", SignOutView.as_view()),
]