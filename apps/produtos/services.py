"""ProdutoService - regras de negócio de produto."""
from decimal import Decimal

from apps.core.exceptions import PrecoInvalidoError
from .repositories import ProdutoRepository

class ProdutoService:

    def __init__(self, repo: ProdutoRepository | None = None):
        self.repo = repo or ProdutoRepository()

    def _validar_preco(self, dados: dict):
        preco = dados.get("preco")
        if preco is not None and Decimal(str(preco)) < 0:
            raise PrecoInvalidoError()

    def criar(self, dados: dict):
        self._validar_preco(dados)
        return self.repo.criar(**dados)

    def atualizar(self, produto_id: int, dados: dict):
        produto = self.repo.por_id(produto_id)
        if not produto:
            return None
        self._validar_preco(dados)
        return self.repo.atualizar(produto, **dados)

    def remover(self, produto_id: int) -> bool:
        produto = self.repo.por_id(produto_id)
        if not produto:
            return False
        # Em vez de deletar fisicamente, faz soft-delete (ativo=False)
        # quando o produto já tiver vendas. Aqui mantemos delete simples.
        if produto.itens_venda.exists():
            produto.ativo = False
            produto.save(update_fields=["ativo", "atualizado_em"])
        else:
            self.repo.remover(produto)
        return True

    def estoque_baixo(self):
        return self.repo.estoque_baixo()
