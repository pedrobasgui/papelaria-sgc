"""
URLs raiz do Papelaria SGC.

Estrutura:
    /admin/               -> Django Admin
    /api/auth/            -> Login, refresh, recuperação de senha
    /api/clientes/        -> CRUD de clientes
    /api/produtos/        -> CRUD de produtos
    /api/vendas/          -> CRUD de vendas
    /api/relatorios/      -> Relatórios e gráficos
    /api/docs/            -> Swagger UI
    /api/schema/          -> Schema OpenAPI
    /                     -> Interface web (Django templates)
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # API REST
    path("api/auth/",       include("apps.usuarios.urls")),
    path("api/clientes/",   include("apps.clientes.urls")),
    path("api/produtos/",   include("apps.produtos.urls")),
    path("api/vendas/",     include("apps.vendas.urls")),
    path("api/relatorios/", include("apps.relatorios.urls")),

    # Documentação OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/",
         SpectacularSwaggerView.as_view(url_name="schema"),
         name="swagger-ui"),
    path("api/redoc/",
         SpectacularRedocView.as_view(url_name="schema"),
         name="redoc"),

    # Interface web (consome a API)
    path("", include("apps.web.urls")),
]

handler404 = "apps.web.views.handler404"