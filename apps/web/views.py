"""
Views da interface web (templates).

Estas views apenas servem o HTML; o JavaScript embutido na página
faz as chamadas à API REST com o token JWT armazenado no localStorage.
"""
from django.shortcuts import render

def login_view(request):
    return render(request, "registration/login.html")

def dashboard_view(request):
    return render(request, "dashboard.html")

# Clientes
def clientes_listar(request):
    return render(request, "clientes/listar.html")

def clientes_form(request, cliente_id=None):
    return render(request, "clientes/form.html",
                  {"cliente_id": cliente_id})

# Produtos
def produtos_listar(request):
    return render(request, "produtos/listar.html")

def produtos_form(request, produto_id=None):
    return render(request, "produtos/form.html",
                  {"produto_id": produto_id})

# Vendas
def vendas_listar(request):
    return render(request, "vendas/listar.html")

def vendas_nova(request):
    return render(request, "vendas/nova.html")

def venda_detalhe(request, venda_id):
    return render(request, "vendas/detalhe.html",
                  {"venda_id": venda_id})

# Relatórios
def relatorios_index(request):
    return render(request, "relatorios/index.html")

def recuperar_senha_view(request):
    return render(request, "registration/recuperar_senha.html")


def redefinir_senha_view(request):
    return render(request, "registration/redefinir_senha.html")

def handler404(request, exception=None):
    return render(request, "errors/404.html", status=404)

def handler500(request):
    return render(request, "errors/500.html", status=500)