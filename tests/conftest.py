"""Fixtures pytest compartilhadas pelos testes."""
import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from apps.clientes.models import Cliente
from apps.produtos.models import Produto

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", email="admin@papel.com",
        password="senha123", perfil="ADMIN", is_staff=True
    )

@pytest.fixture
def funcionario_user(db):
    return User.objects.create_user(
        username="func", email="func@papel.com",
        password="senha123", perfil="FUNCIONARIO"
    )

@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def func_client(api_client, funcionario_user):
    api_client.force_authenticate(user=funcionario_user)
    return api_client

@pytest.fixture
def cliente(db):
    return Cliente.objects.create(
        nome="Ana Beatriz", cpf="529.982.247-25",
        email="ana@email.com", telefone="(61) 99999-0000",
        endereco="QN 1, Brasília/DF",
    )

@pytest.fixture
def produto(db):
    return Produto.objects.create(
        nome="Caderno 100 folhas", descricao="Caderno espiral",
        preco=Decimal("19.90"), estoque=50, estoque_minimo=10,
    )

@pytest.fixture
def produto_baixo(db):
    return Produto.objects.create(
        nome="Borracha", descricao="Borracha branca",
        preco=Decimal("1.50"), estoque=2, estoque_minimo=10,
    )
