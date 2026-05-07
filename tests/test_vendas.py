"""Testes do fluxo de vendas (regras críticas)."""
import pytest
from decimal import Decimal

from apps.vendas.models import Venda
from apps.vendas.services import VendaService
from apps.core.exceptions import (
    VendaSemItensError, EstoqueInsuficienteError,
    VendaJaCanceladaError, ClientePossuiVendasError,
)
from apps.clientes.services import ClienteService

@pytest.mark.django_db
class TestVendaService:

    def test_criar_venda_simples(self, admin_user, cliente, produto):
        s = VendaService()
        venda = s.criar_venda(
            cliente_id=cliente.id, usuario=admin_user,
            itens=[{"produto_id": produto.id, "quantidade": 3}]
        )
        assert venda.id is not None
        assert venda.valor_total == Decimal("19.90") * 3
        produto.refresh_from_db()
        assert produto.estoque == 47   # 50 - 3

    def test_venda_sem_itens(self, admin_user, cliente):
        s = VendaService()
        with pytest.raises(VendaSemItensError):
            s.criar_venda(
                cliente_id=cliente.id, usuario=admin_user, itens=[]
            )

    def test_estoque_insuficiente(self, admin_user, cliente, produto):
        s = VendaService()
        with pytest.raises(EstoqueInsuficienteError):
            s.criar_venda(
                cliente_id=cliente.id, usuario=admin_user,
                itens=[{"produto_id": produto.id, "quantidade": 9999}]
            )

    def test_cancelar_venda_devolve_estoque(self, admin_user, cliente, produto):
        s = VendaService()
        venda = s.criar_venda(
            cliente_id=cliente.id, usuario=admin_user,
            itens=[{"produto_id": produto.id, "quantidade": 5}]
        )
        produto.refresh_from_db()
        assert produto.estoque == 45

        s.cancelar_venda(venda.id)
        produto.refresh_from_db()
        assert produto.estoque == 50
        venda.refresh_from_db()
        assert venda.status == Venda.Status.CANCELADA

    def test_cancelar_venda_ja_cancelada(self, admin_user, cliente, produto):
        s = VendaService()
        venda = s.criar_venda(
            cliente_id=cliente.id, usuario=admin_user,
            itens=[{"produto_id": produto.id, "quantidade": 1}]
        )
        s.cancelar_venda(venda.id)
        with pytest.raises(VendaJaCanceladaError):
            s.cancelar_venda(venda.id)

    def test_cliente_com_vendas_nao_pode_ser_removido(
        self, admin_user, cliente, produto
    ):
        s = VendaService()
        s.criar_venda(
            cliente_id=cliente.id, usuario=admin_user,
            itens=[{"produto_id": produto.id, "quantidade": 1}]
        )
        cs = ClienteService()
        with pytest.raises(ClientePossuiVendasError):
            cs.remover(cliente.id)

@pytest.mark.django_db
class TestVendaAPI:

    def test_criar_venda_via_api(self, admin_client, cliente, produto):
        r = admin_client.post("/api/vendas/", {
            "cliente_id": cliente.id,
            "itens": [{"produto_id": produto.id, "quantidade": 2}]
        }, format="json")
        assert r.status_code == 201
        assert float(r.json()["valor_total"]) == 39.80

    def test_listar_vendas(self, admin_client, cliente, produto, admin_user):
        VendaService().criar_venda(
            cliente_id=cliente.id, usuario=admin_user,
            itens=[{"produto_id": produto.id, "quantidade": 1}]
        )
        r = admin_client.get("/api/vendas/")
        assert r.status_code == 200
        data = r.json().get("results", r.json())
        assert len(data) >= 1

    def test_relatorio_anual(self, admin_client):
        r = admin_client.get("/api/relatorios/anual/?ano=2026")
        assert r.status_code == 200
        body = r.json()
        assert len(body["labels"]) == 12
        assert len(body["valores"]) == 12

    def test_funcionario_pode_vender(self, func_client, cliente, produto):
        r = func_client.post("/api/vendas/", {
            "cliente_id": cliente.id,
            "itens": [{"produto_id": produto.id, "quantidade": 1}]
        }, format="json")
        assert r.status_code == 201
