"""Testes de clientes (model, service e API)."""
import pytest
from apps.clientes.models import Cliente, validar_cpf
from apps.clientes.services import ClienteService
from apps.core.exceptions import (
    CPFDuplicadoError, ClientePossuiVendasError
)

class TestValidarCPF:
    def test_cpf_valido(self):
        assert validar_cpf("529.982.247-25") is True

    def test_cpf_invalido(self):
        assert validar_cpf("111.111.111-11") is False

    def test_cpf_curto(self):
        assert validar_cpf("123") is False

@pytest.mark.django_db
class TestClienteService:

    def test_criar_cliente(self):
        s = ClienteService()
        c = s.criar({
            "nome": "João", "cpf": "529.982.247-25",
            "email": "j@email.com",
        })
        assert c.id is not None
        assert c.nome == "João"

    def test_cpf_duplicado_lanca_excecao(self, cliente):
        s = ClienteService()
        with pytest.raises(CPFDuplicadoError):
            s.criar({
                "nome": "Outro", "cpf": cliente.cpf,
                "email": "x@email.com",
            })

    def test_remover_cliente_sem_vendas(self, cliente):
        s = ClienteService()
        assert s.remover(cliente.id) is True
        assert not Cliente.objects.filter(pk=cliente.id).exists()

    def test_cpf_invalido_lanca_excecao(self):
        from apps.core.exceptions import CPFInvalidoError
        s = ClienteService()
        with pytest.raises(CPFInvalidoError):
            s.criar({
                "nome": "Teste", "cpf": "123.456.789-00",
                "email": "t@email.com",
            })

@pytest.mark.django_db
class TestClienteAPI:

    def test_listar_clientes(self, admin_client, cliente):
        r = admin_client.get("/api/clientes/")
        assert r.status_code == 200
        data = r.json().get("results", r.json())
        assert any(c["cpf"] == cliente.cpf for c in data)

    def test_criar_cliente(self, admin_client):
        r = admin_client.post("/api/clientes/", {
            "nome": "Carlos", "cpf": "248.438.034-80",
            "email": "carlos@email.com",
        }, format="json")
        assert r.status_code == 201
        assert r.json()["nome"] == "Carlos"

    def test_criar_cpf_duplicado(self, admin_client, cliente):
        r = admin_client.post("/api/clientes/", {
            "nome": "Duplicado", "cpf": cliente.cpf,
        }, format="json")
        assert r.status_code == 409
        assert r.json()["codigo"] == "CPF_DUPLICADO"

    def test_atualizar(self, admin_client, cliente):
        r = admin_client.patch(
            f"/api/clientes/{cliente.id}/",
            {"nome": "Ana B. Souza"}, format="json"
        )
        assert r.status_code == 200
        assert r.json()["nome"] == "Ana B. Souza"

    def test_remover(self, admin_client, cliente):
        r = admin_client.delete(f"/api/clientes/{cliente.id}/")
        assert r.status_code == 200

    def test_acesso_sem_autenticacao(self, api_client):
        r = api_client.get("/api/clientes/")
        assert r.status_code == 401
