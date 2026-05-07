"""
VendaService - regras de negócio de venda.

Operações críticas envolvem MULTIPLAS tabelas (vendas, itens, produtos)
e são executadas em transação atômica para garantir consistência:
- criar_venda: valida estoque, cria venda + itens, debita estoque, recalcula total
- cancelar_venda: marca como CANCELADA e devolve estoque
"""
from decimal import Decimal
from typing import Iterable

from django.db import transaction

from apps.core.exceptions import (
    VendaSemItensError,
    VendaJaCanceladaError,
    EstoqueInsuficienteError,
)
from apps.produtos.repositories import ProdutoRepository

from .models import Venda, ItemVenda
from .repositories import VendaRepository

class VendaService:

    def __init__(self,
                 venda_repo: VendaRepository | None = None,
                 produto_repo: ProdutoRepository | None = None):
        self.venda_repo = venda_repo or VendaRepository()
        self.produto_repo = produto_repo or ProdutoRepository()

    @transaction.atomic
    def criar_venda(self,
                    cliente_id: int,
                    usuario,
                    itens: Iterable[dict],
                    observacao: str | None = None) -> Venda:
        """
        Cria uma venda completa. Operação atômica:
        - Se qualquer item falhar (estoque, produto inexistente),
          NADA é persistido.
        """
        itens = list(itens)
        if not itens:
            raise VendaSemItensError()

        # 1) Cria cabeçalho da venda
        venda = Venda.objects.create(
            cliente_id=cliente_id,
            usuario=usuario,
            valor_total=Decimal("0.00"),
            observacao=observacao,
            status=Venda.Status.CONCLUIDA,
        )

        total = Decimal("0.00")

        # 2) Para cada item: bloqueia produto, valida estoque, debita
        for item in itens:
            produto_id = item["produto_id"]
            quantidade = int(item["quantidade"])

            if quantidade <= 0:
                raise VendaSemItensError(
                    "A quantidade de cada item deve ser positiva."
                )

            produto = self.produto_repo.por_id_lock(produto_id)
            if not produto:
                raise EstoqueInsuficienteError(
                    f"Produto {produto_id} não encontrado.",
                    detalhes={"produto_id": produto_id}
                )

            if not produto.tem_estoque(quantidade):
                raise EstoqueInsuficienteError(
                    detalhes={
                        "produto_id": produto.id,
                        "produto": produto.nome,
                        "estoque_atual": produto.estoque,
                        "solicitado": quantidade,
                    }
                )

            preco = item.get("preco_unitario") or produto.preco

            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco,
            )

            produto.debitar_estoque(quantidade)
            total += Decimal(preco) * Decimal(quantidade)

        # 3) Atualiza valor_total
        venda.valor_total = total
        venda.save(update_fields=["valor_total"])

        return venda

    @transaction.atomic
    def cancelar_venda(self, venda_id: int) -> Venda:
        venda = (
            Venda.objects
            .select_for_update()
            .prefetch_related("itens__produto")
            .filter(pk=venda_id)
            .first()
        )
        if not venda:
            return None
        if venda.esta_cancelada:
            raise VendaJaCanceladaError()

        for item in venda.itens.all():
            produto = self.produto_repo.por_id_lock(item.produto_id)
            if produto:
                produto.creditar_estoque(item.quantidade)

        venda.status = Venda.Status.CANCELADA
        venda.save(update_fields=["status"])
        return venda

    def listar(self, filtros: dict | None = None):
        return self.venda_repo.listar(filtros or {})

    def detalhe(self, venda_id: int):
        return self.venda_repo.por_id(venda_id)
