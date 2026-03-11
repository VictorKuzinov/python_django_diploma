from django.urls import path
from .views import ProfileView, ProfileAvatarView, ProfilePasswordView

urlpatterns = [
    path("profile", ProfileView.as_view(), name="profile"),
    path("profile/", ProfileView.as_view()),
path("profile/", ProfileView.as_view()),
    path("profile/avatar", ProfileAvatarView.as_view(), name="profile-avatar"),
    path("profile/avatar/", ProfileAvatarView.as_view()),
    path("profile/password", ProfilePasswordView.as_view(), name="profile-password"),
    path("profile/password/", ProfilePasswordView.as_view()),
]
