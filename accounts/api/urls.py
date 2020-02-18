from django.urls import path
from .views import RegisterAPIView, AuthAPIView, LogoutAPIView, UserListAPIView

app_name = "accounts"
urlpatterns = [
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("auth/", AuthAPIView.as_view(), name="auth"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("all/", UserListAPIView.as_view(), name="users"),
]
