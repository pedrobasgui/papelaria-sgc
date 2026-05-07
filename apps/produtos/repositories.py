"""Repository de Produto - encapsula consultas e persistência."""
from typing import Optional
from django.db.models import F, QuerySet
from .models import Produto

class ProdutoRepository:

    @staticmethod
    def listar(busca: Optional[str] = None,
               apenas_ativos: bool = False) -> QuerySet[Produto]:
        qs = Produto.objects.all()
        if apenas_ativos:
            qs = qs.filter(ativo=True)
        if busca:
            qs = qs.filter(nome__icontains=busca)
        return qs.order_by("nome")

    @staticmethod
    def por_id(produto_id: int) -> Optional[Produto]:
        return Produto.objects.filter(pk=produto_id).first()

    @staticmethod
    def por_id_lock(produto_id: int) -> Optional[Produto]:
        """Versão com SELECT FOR UPDATE (uso em transações de venda)."""
        return Produto.objects.select_for_update().filter(pk=produto_id).first()

    @staticmethod
    def estoque_baixo() -> QuerySet[Produto]:
        return Produto.objects.filter(
            ativo=True, estoque__lte=F("estoque_minimo")
        ).order_by("estoque")

    @staticmethod
    def criar(**dados) -> Produto:
        p = Produto(**dados)
        p.full_clean()
        p.save()
        return p

    @staticmethod
    def atualizar(produto: Produto, **dados) -> Produto:
        for k, v in dados.items():
            setattr(produto, k, v)
        produto.full_clean()
        produto.save()
        return produto

    @staticmethod
    def remover(produto: Produto) -> None:
        produto.delete()
