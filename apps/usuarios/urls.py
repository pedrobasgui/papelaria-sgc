"""URLs do app usuarios."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView, LogoutView, MeView,
    TrocarSenhaView, RecuperarSenhaView, RedefinirSenhaView, UsuarioViewSet,
)

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = [
    path("login/",            LoginView.as_view(),    name="auth-login"),
    path("logout/",           LogoutView.as_view(),   name="auth-logout"),
    path("refresh/",          TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/",               MeView.as_view(),       name="auth-me"),
    path("trocar-senha/",     TrocarSenhaView.as_view(),    name="auth-trocar-senha"),
    path("recuperar-senha/",  RecuperarSenhaView.as_view(), name="auth-recuperar"),
    path("redefinir-senha/",  RedefinirSenhaView.as_view(), name="auth-redefinir"),
    path("",                  include(router.urls)),
]
