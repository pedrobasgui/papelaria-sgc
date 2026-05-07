from django.urls import path
from . import views

urlpatterns = [
    path("",        views.login_view,      name="web-login"),
    path("login/",  views.login_view,      name="web-login-alt"),
    path("dashboard/", views.dashboard_view, name="web-dashboard"),

    # Clientes
    path("clientes/",         views.clientes_listar, name="web-clientes"),
    path("clientes/novo/",    views.clientes_form,   name="web-clientes-novo"),
    path("clientes/<int:cliente_id>/editar/",
         views.clientes_form,   name="web-clientes-editar"),

    # Produtos
    path("produtos/",         views.produtos_listar, name="web-produtos"),
    path("produtos/novo/",    views.produtos_form,   name="web-produtos-novo"),
    path("produtos/<int:produto_id>/editar/",
         views.produtos_form,   name="web-produtos-editar"),

    # Vendas
    path("vendas/",           views.vendas_listar,   name="web-vendas"),
    path("vendas/nova/",      views.vendas_nova,     name="web-vendas-nova"),
    path("vendas/<int:venda_id>/",
         views.venda_detalhe,   name="web-venda-detalhe"),

    # Relatórios
    path("relatorios/",       views.relatorios_index, name="web-relatorios"),
]
