"""Testes de produtos."""
import pytest
from decimal import Decimal
from apps.produtos.models import Produto
from apps.produtos.services import ProdutoService
from apps.core.exceptions import (
    PrecoInvalidoError, EstoqueInsuficienteError
)

@pytest.mark.django_db
class TestProdutoModel:

    def test_tem_estoque(self, produto):
        assert produto.tem_estoque(10) is True
        assert produto.tem_estoque(1000) is False

    def test_alerta_estoque_baixo(self, produto, produto_baixo):
        assert produto.alerta_estoque_baixo() is False
        assert produto_baixo.alerta_estoque_baixo() is True

    def test_debitar_estoque(self, produto):
        produto.debitar_estoque(5)
        assert produto.estoque == 45

    def test_debitar_estoque_insuficiente(self, produto):
        with pytest.raises(EstoqueInsuficienteError):
            produto.debitar_estoque(1000)

    def test_creditar_estoque(self, produto):
        produto.creditar_estoque(10)
        assert produto.estoque == 60

@pytest.mark.django_db
class TestProdutoService:

    def test_preco_negativo(self):
        s = ProdutoService()
        with pytest.raises(PrecoInvalidoError):
            s.criar({"nome": "X", "preco": Decimal("-1.00"), "estoque": 5})

    def test_criar_produto(self):
        s = ProdutoService()
        p = s.criar({
            "nome": "Caneta", "preco": Decimal("2.50"),
            "estoque": 100, "estoque_minimo": 20
        })
        assert p.id is not None

@pytest.mark.django_db
class TestProdutoAPI:

    def test_listar(self, admin_client, produto):
        r = admin_client.get("/api/produtos/")
        assert r.status_code == 200

    def test_funcionario_pode_ler(self, func_client, produto):
        r = func_client.get("/api/produtos/")
        assert r.status_code == 200

    def test_funcionario_nao_pode_criar(self, func_client):
        r = func_client.post("/api/produtos/", {
            "nome": "Teste", "preco": "1.00", "estoque": 1
        }, format="json")
        assert r.status_code == 403

    def test_admin_pode_criar(self, admin_client):
        r = admin_client.post("/api/produtos/", {
            "nome": "Lápis", "preco": "1.50",
            "estoque": 100, "estoque_minimo": 10,
        }, format="json")
        assert r.status_code == 201

    def test_estoque_baixo(self, admin_client, produto_baixo):
        r = admin_client.get("/api/produtos/estoque-baixo/")
        assert r.status_code == 200
        ids = [p["id"] for p in r.json()]
        assert produto_baixo.id in ids

    def test_preco_zero_e_aceito(self):
            s = ProdutoService()
            p = s.criar({
                "nome": "Brinde",
                "preco": 0,
                "estoque": 10,
                "estoque_minimo": 2,
            })
            assert p.id is not None

    def test_inativar_produto_com_vendas(self, admin_user, cliente, produto):
        from apps.vendas.services import VendaService
        VendaService().criar_venda(
            cliente_id=cliente.id, usuario=admin_user,
            itens=[{"produto_id": produto.id, "quantidade": 1}]
        )
        s = ProdutoService()
        s.remover(produto.id)
        produto.refresh_from_db()
        assert produto.ativo is False