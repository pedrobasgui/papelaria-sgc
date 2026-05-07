from django.urls import path
from .views import (
    RelatorioPorPeriodoView, RelatorioPorClienteView,
    RelatorioAnualView, TopProdutosView,
)

urlpatterns = [
    path("por-periodo/",          RelatorioPorPeriodoView.as_view(),
         name="rel-periodo"),
    path("por-cliente/<int:cliente_id>/", RelatorioPorClienteView.as_view(),
         name="rel-cliente"),
    path("anual/",                RelatorioAnualView.as_view(),
         name="rel-anual"),
    path("top-produtos/",         TopProdutosView.as_view(),
         name="rel-top-produtos"),
]
